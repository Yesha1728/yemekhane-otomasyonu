"""
İŞ KURALLARI

Arayüz (JavaScript) hiçbir iş kuralı bilmez; yalnızca buradan gelen sonuçları gösterir.
"""


def kullanici_fiyati(rol, ogrenci_fiyati, personel_fiyati):
    """Öğrenci öğrenci fiyatını, personel ve yönetici personel fiyatını öder."""
    return ogrenci_fiyati if rol == "ogrenci" else personel_fiyati


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