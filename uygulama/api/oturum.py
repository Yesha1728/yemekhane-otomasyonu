"""
OTURUMLAR (Redis)

Anahtar : oturum:{jeton}
Değer   : kullanıcı özeti (JSON)
Süre    : 30 dakika; her başarılı istekte yeniden 30 dakikaya uzatılır
Silinme : çıkış yapıldığında (ya da süre dolunca Redis kendisi siler)

Oturumlar Redis'te durduğu için uygulama container'ı yeniden başlasa da düşmez.
"""
import json
import secrets

from .veri import redis_baglanti

OMUR_SANIYE = 30 * 60
ONEK = "oturum:"


def olustur(kullanici):
    """Yeni oturum açar, rastgele bir jeton döndürür."""
    jeton = secrets.token_urlsafe(32)
    redis_baglanti.istemci().set(ONEK + jeton, json.dumps(kullanici, ensure_ascii=False), ex=OMUR_SANIYE)
    return jeton


def getir(jeton):
    """Jetonun kullanıcısını verir ve süreyi yeniler. Geçersiz ya da süresi dolmuşsa None."""
    if not jeton:
        return None
    # GETEX: değeri okur ve süreyi aynı anda, tek komutla yeniler.
    ham = redis_baglanti.istemci().getex(ONEK + jeton, ex=OMUR_SANIYE)
    return json.loads(ham) if ham else None


def sil(jeton):
    if jeton:
        redis_baglanti.istemci().delete(ONEK + jeton)