import datetime
import decimal
import json
import logging
from functools import wraps

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from . import kimlik
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
                        json_dumps_params={"ensure_ascii": False},
                        content_type="application/json; charset=utf-8")


def hata_yaniti(mesaj, durum):
    return yanit({"hata": mesaj}, durum)


def uc_nokta(metodlar, giris=True, roller=None):
    """
    Her denetleyici fonksiyonunu saran "ceket":
      1) HTTP yöntemini denetler,
      2) giris=True ise oturumu ve (verildiyse) rolü denetler; kullanıcı istek.kullanici içine konur,
      3) fırlatılan hataları JSON yanıtına çevirir:
         BulunamadiHatasi 404, YetkiHatasi 401, IsKuraliHatasi 400, diğerleri 500.
    """
    if isinstance(metodlar, str):
        metodlar = (metodlar,)

    def sarmalayici(islev):
        @wraps(islev)
        def sarili(istek, *args, **kwargs):
            if istek.method not in metodlar:
                return hata_yaniti("Bu yol için izin verilen yöntem: " + ", ".join(metodlar), 405)
            if giris:
                kullanici = kimlik.istekten_kullanici(istek)
                if kullanici is None:
                    return hata_yaniti("Oturum açmanız gerekiyor.", 401)
                if roller and kullanici["rol"] not in roller:
                    return hata_yaniti("Bu işlem için yetkiniz yok.", 403)
                istek.kullanici = kullanici
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

def taze_mi(istek):
    """?taze=1 verilirse okuma kaynaktan yapılır (kullanıcı az önce yazma yaptıysa)."""
    return istek.GET.get("taze") == "1"

def tamsayi(deger, ad, varsayilan=None):
    """Girdiyi tam sayıya çevirir. Boşsa varsayılanı verir (varsayılan yoksa hata)."""
    if deger is None or deger == "":
        if varsayilan is None:
            raise IsKuraliHatasi(f"{ad} gerekli.")
        return varsayilan
    if isinstance(deger, bool):
        raise IsKuraliHatasi(f"{ad} sayı olmalı.")
    try:
        return int(deger)
    except (TypeError, ValueError):
        raise IsKuraliHatasi(f"{ad} sayı olmalı.") from None


def tarih(deger, ad, varsayilan=None):
    """Girdiyi YYYY-AA-GG tarihine çevirir. Boşsa varsayılanı verir (varsayılan yoksa hata)."""
    if deger is None or deger == "":
        if varsayilan is None:
            raise IsKuraliHatasi(f"{ad} gerekli.")
        return varsayilan
    try:
        return datetime.date.fromisoformat(str(deger))
    except ValueError:
        raise IsKuraliHatasi(f"{ad} YYYY-AA-GG biçiminde olmalı.") from None