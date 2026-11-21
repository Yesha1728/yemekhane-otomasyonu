import datetime
import decimal
import json
import logging
from functools import wraps

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from .veri.hatalar import BulunamadiHatasi, IsKuraliHatasi, YetkiHatasi

gunluk = logging.getLogger("yemekhane.api")


class _Kodlayici(DjangoJSONEncoder):
    """Decimal sayıları JSON sayısı yapar (varsayılan metin olurdu), timedelta'yı SS:DD verir."""

    def default(self, nesne):
        if isinstance(nesne, decimal.Decimal):
            return float(nesne)
        if isinstance(nesne, datetime.timedelta):
            toplam = int(nesne.total_seconds())
            return "%02d:%02d" % (toplam // 3600, toplam % 3600 // 60)
        return super().default(nesne)


def yanit(veri, durum=200):
    return JsonResponse(veri, status=durum, encoder=_Kodlayici, safe=False,
                        json_dumps_params={"ensure_ascii": False})


def hata_yaniti(mesaj, durum):
    return yanit({"hata": mesaj}, durum)


def uc_nokta(metodlar):
    if isinstance(metodlar, str):
        metodlar = (metodlar,)

    def sarmalayici(islev):
        @wraps(islev)
        def sarili(istek, *args, **kwargs):
            if istek.method not in metodlar:
                return hata_yaniti("Bu yol için izin verilen yöntem: " + ", ".join(metodlar), 405)
            try:
                return islev(istek, *args, **kwargs)
            except BulunamadiHatasi as h:
                return hata_yaniti(str(h), 404)
            except YetkiHatasi as h:
                return hata_yaniti(str(h), 401)
            except IsKuraliHatasi as h:
                return hata_yaniti(str(h), 400)
            except Exception:
                gunluk.exception("Beklenmeyen hata: %s %s", istek.method, istek.path)
                return hata_yaniti("Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.", 500)
        return sarili
    return sarmalayici

def govde(istek):
    """JSON gövdesini sözlük olarak okur."""
    try:
        veri = json.loads(istek.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        raise IsKuraliHatasi("İstek gövdesi geçerli JSON değil.") from None
    if not isinstance(veri, dict):
        raise IsKuraliHatasi("İstek gövdesi bir JSON nesnesi olmalı.")
    return veri