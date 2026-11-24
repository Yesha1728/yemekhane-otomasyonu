"""
İŞ KURALLARI

Arayüz (JavaScript) hiçbir iş kuralı bilmez; yalnızca buradan gelen sonuçları gösterir.
"""
from decimal import ROUND_HALF_UP, Decimal


def kullanici_fiyati(rol, ogrenci_fiyati, personel_fiyati):
    """Öğrenci öğrenci fiyatını, personel ve yönetici personel fiyatını öder."""
    return ogrenci_fiyati if rol == "ogrenci" else personel_fiyati


def yarim_fiyat(tam_fiyat):
    """Yarım porsiyon tam fiyatın %60'ıdır (sp_rezervasyon_yap ile aynı kural; son karar yordamındır)."""
    return (Decimal(str(tam_fiyat)) * Decimal("0.60")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def rezervasyon_yapilabilir(suresi_doldu, bos_yer, rezervasyon_durumu):
    """
    Düğme aktif mi? Son saat geçmediyse, boş yer varsa ve kullanıcının bu menüde
    aktif ya da kullanılmış rezervasyonu yoksa. (İptal edilmiş kayıt yeniden rezerve edilebilir.)
    Son karar yine de sp_rezervasyon_yap yordamındadır.
    """
    if suresi_doldu or bos_yer <= 0:
        return False
    return rezervasyon_durumu not in ("aktif", "kullanildi")


def pasiflik_nedeni(suresi_doldu, bos_yer, rezervasyon_durumu):
    """Düğme pasifse kullanıcıya gösterilecek kısa neden; aktifse None."""
    if rezervasyon_durumu in ("aktif", "kullanildi"):
        return "Rezervasyonunuz var"
    if suresi_doldu:
        return "Süre doldu"
    if bos_yer <= 0:
        return "Dolu"
    return None


def iptal_edilebilir(durum, suresi_doldu):
    """Yalnızca aktif ve son saati geçmemiş rezervasyon iptal edilebilir."""
    return durum == "aktif" and not suresi_doldu