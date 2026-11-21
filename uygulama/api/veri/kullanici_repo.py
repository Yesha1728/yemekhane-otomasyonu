from . import baglanti


def eposta_ile_bul(eposta):
    """Giriş için kullanıcıyı bulur. Kaynaktan okunur: küçük bir sorgudur ve her zaman güncel olmalıdır."""
    with baglanti.yazma_baglantisi() as b:
        return baglanti.tek_satir(
            b,
            "SELECT id, ad, soyad, eposta, sifre_hash, rol, aktif FROM kullanicilar WHERE eposta = %s",
            (eposta,),
        )