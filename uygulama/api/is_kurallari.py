"""
İŞ KURALLARI

Arayüz (JavaScript) hiçbir iş kuralı bilmez; yalnızca buradan gelen sonuçları gösterir.
"""


def kullanici_fiyati(rol, ogrenci_fiyati, personel_fiyati):
    """Öğrenci öğrenci fiyatını, personel ve yönetici personel fiyatını öder."""
    return ogrenci_fiyati if rol == "ogrenci" else personel_fiyati