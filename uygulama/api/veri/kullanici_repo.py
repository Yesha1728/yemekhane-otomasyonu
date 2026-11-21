from . import baglanti


def eposta_ile_bul(eposta):
    """Giriş için kullanıcıyı bulur. Kaynaktan okunur: küçük bir sorgudur ve her zaman güncel olmalıdır."""
    with baglanti.yazma_baglantisi() as b:
        return baglanti.tek_satir(
            b,
            "SELECT id, ad, soyad, eposta, sifre_hash, rol, aktif FROM kullanicilar WHERE eposta = %s",
            (eposta,),
        )


def bakiye_getir(kullanici_id, taze=False):
    with baglanti.okuma_baglantisi(taze) as b:
        satir = baglanti.tek_satir(b, "SELECT bakiye FROM kullanicilar WHERE id = %s", (kullanici_id,))
    return satir["bakiye"] if satir else None


def bakiye_hareketleri(kullanici_id, taze=False, limit=50):
    with baglanti.okuma_baglantisi(taze) as b:
        return baglanti.sorgula(
            b,
            """SELECT id, tur, tutar, rezervasyon_id, aciklama, olusturma
                 FROM bakiye_hareketleri
                WHERE kullanici_id = %s
                ORDER BY id DESC
                LIMIT %s""",
            (kullanici_id, limit),
        )


def bakiye_yukle(kullanici_id, tutar):
    """sp_bakiye_yukle · yazma (kaynak). Döner: hareket_id, bakiye"""
    with baglanti.yazma_baglantisi() as b:
        return baglanti.yordam_cagir(b, "sp_bakiye_yukle", kullanici_id, tutar)