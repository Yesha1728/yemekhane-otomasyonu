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

def alerjen_listesi(taze=False):
    """Tüm alerjenler (id, ad). Listeleme: replika."""
    with baglanti.okuma_baglantisi(taze) as b:
        return baglanti.sorgula(b, "SELECT id, ad FROM alerjenler ORDER BY ad")


def alerjenleri_getir(kullanici_id, taze=False):
    """Kullanıcının seçtiği alerjen numaraları. Listeleme: replika."""
    with baglanti.okuma_baglantisi(taze) as b:
        satirlar = baglanti.sorgula(
            b,
            "SELECT alerjen_id FROM kullanici_alerjenleri WHERE kullanici_id = %s ORDER BY alerjen_id",
            (kullanici_id,),
        )
    return [s["alerjen_id"] for s in satirlar]


def alerjenleri_kaydet(kullanici_id, alerjen_idler):
    """Kullanıcının alerjen seçimini bütünüyle değiştirir (sil + yeniden ekle, tek işlemde). Yazma: kaynak."""
    with baglanti.yazma_baglantisi() as b:
        b.begin()
        try:
            with b.cursor() as imlec:
                imlec.execute("DELETE FROM kullanici_alerjenleri WHERE kullanici_id = %s", (kullanici_id,))
                if alerjen_idler:
                    imlec.executemany(
                        "INSERT INTO kullanici_alerjenleri (kullanici_id, alerjen_id) VALUES (%s, %s)",
                        [(kullanici_id, a) for a in alerjen_idler],
                    )
            b.commit()
        except Exception:
            b.rollback()
            raise