import secrets
import threading
import time

OMUR_SANIYE = 30 * 60

_depo = {}
_kilit = threading.Lock()


def olustur(kullanici):
    """Yeni oturum açar, rastgele bir jeton döndürür."""
    jeton = secrets.token_urlsafe(32)
    with _kilit:
        _depo[jeton] = {"kullanici": kullanici, "bitis": time.time() + OMUR_SANIYE}
    return jeton


def getir(jeton):
    """Jetonun kullanıcısını verir ve süreyi yeniler. Geçersiz ya da süresi dolmuşsa None."""
    if not jeton:
        return None
    simdi = time.time()
    with _kilit:
        kayit = _depo.get(jeton)
        if kayit is None:
            return None
        if kayit["bitis"] < simdi:
            del _depo[jeton]
            return None
        kayit["bitis"] = simdi + OMUR_SANIYE
        return kayit["kullanici"]


def sil(jeton):
    with _kilit:
        _depo.pop(jeton, None)