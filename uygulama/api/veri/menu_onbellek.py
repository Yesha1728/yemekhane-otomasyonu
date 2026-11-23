"""
MENÜ ÖNBELLEĞİ (Redis)

Anahtar : menu:{yemekhane_id}:{tarih}:{ogun_id}
Değer   : menünün içeriği (JSON): yemekler, kalori, alerjen, fiyatlar
Süre    : menünün gününün sonuna kadar
Silinme : yönetici o menüyü değiştirdiğinde

Önbellek bir hızlandırıcıdır, doğruluk kaynağı değildir. Redis'e ulaşılamazsa uygulama
çalışmaya devam eder: hata günlüğe yazılır ve veri doğrudan veritabanından okunur.
"""
import datetime
import decimal
import json
import logging

import redis

from . import redis_baglanti

gunluk = logging.getLogger("yemekhane.onbellek")

EN_AZ_SANIYE = 60


def anahtar(yemekhane_id, tarih, ogun_id):
    return f"menu:{yemekhane_id}:{tarih}:{ogun_id}"


def _json_cevir(nesne):
    if isinstance(nesne, decimal.Decimal):
        return float(nesne)
    raise TypeError(f"JSON'a çevrilemeyen tür: {type(nesne)}")


def _omur(tarih):
    """Menünün gününün sonuna (ertesi gün 00:00) kadar kalan saniye; en az 1 dakika."""
    if isinstance(tarih, str):
        tarih = datetime.date.fromisoformat(tarih)
    gun_sonu = datetime.datetime.combine(tarih + datetime.timedelta(days=1), datetime.time.min)
    return max(EN_AZ_SANIYE, int((gun_sonu - datetime.datetime.now()).total_seconds()))


def getir(yemekhane_id, tarih, ogun_id):
    """Önbellekteki menüyü verir; yoksa (ya da Redis'e ulaşılamazsa) None."""
    k = anahtar(yemekhane_id, tarih, ogun_id)
    try:
        ham = redis_baglanti.istemci().get(k)
    except redis.RedisError:
        gunluk.exception("Redis okunamadı, veritabanına gidiliyor: %s", k)
        return None
    if ham is None:
        return None
    return json.loads(ham)


def yaz(yemekhane_id, tarih, ogun_id, menu):
    k = anahtar(yemekhane_id, tarih, ogun_id)
    omur = _omur(tarih)
    try:
        redis_baglanti.istemci().set(k, json.dumps(menu, default=_json_cevir, ensure_ascii=False), ex=omur)
        gunluk.info("Menü veritabanından okundu, önbelleğe yazıldı: %s (süre %d sn)", k, omur)
    except redis.RedisError:
        gunluk.exception("Redis'e yazılamadı: %s", k)


def sil(yemekhane_id, tarih, ogun_id):
    k = anahtar(yemekhane_id, tarih, ogun_id)
    try:
        silinen = redis_baglanti.istemci().delete(k)
        gunluk.info("Menü önbelleği silindi: %s (silinen kayıt: %d)", k, silinen)
    except redis.RedisError:
        gunluk.exception("Önbellek silinemedi, eski menü süre bitene kadar kalabilir: %s", k)