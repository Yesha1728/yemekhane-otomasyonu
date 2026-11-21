from . import baglanti


def bugun(taze=False):
    """Bugünün tarihi (veritabanı saatine göre; saat dilimi karışıklığı olmasın)."""
    with baglanti.okuma_baglantisi(taze) as b:
        return baglanti.tek_satir(b, "SELECT CURDATE() AS bugun")["bugun"]


def yemekhaneler(taze=False):
    with baglanti.okuma_baglantisi(taze) as b:
        return baglanti.sorgula(b, "SELECT id, ad, konum, kapasite FROM yemekhaneler ORDER BY id")


def ogunler(taze=False):
    with baglanti.okuma_baglantisi(taze) as b:
        return baglanti.sorgula(b, "SELECT id, ad, sira FROM ogunler ORDER BY sira")

def menu_icerik(yemekhane_id, tarih, ogun_id, taze=False):
    """
    Bir menünün içeriği (yemekler, kalori, alerjen). Kullanıcıya özel olmayan, değişmeyen kısım.
    Menü yoksa None. Yemekler kategori sırasına göre gelir.
    """
    with baglanti.okuma_baglantisi(taze) as b:
        satirlar = baglanti.sorgula(
            b,
            """SELECT * FROM v_menu_detay
                WHERE yemekhane_id = %s AND tarih = %s AND ogun_id = %s
                ORDER BY kategori_sira, yemek""",
            (yemekhane_id, tarih, ogun_id),
        )
    if not satirlar:
        return None

    ilk = satirlar[0]
    yemekler = []
    for s in satirlar:
        yemekler.append({
            "yemek_id": s["yemek_id"],
            "yemek": s["yemek"],
            "kategori": s["kategori"],
            "kalori": s["kalori"],
            "vejetaryen": bool(s["vejetaryen"]),
            "alerjenler": s["alerjenler"].split(", ") if s["alerjenler"] else [],
            "alerjen_idler": [int(x) for x in s["alerjen_idler"].split(",")] if s["alerjen_idler"] else [],
        })
    return {
        "menu_id": ilk["menu_id"],
        "tarih": ilk["tarih"].isoformat(),
        "yemekhane_id": ilk["yemekhane_id"],
        "yemekhane": ilk["yemekhane"],
        "ogun_id": ilk["ogun_id"],
        "ogun": ilk["ogun"],
        "ogrenci_fiyati": ilk["ogrenci_fiyati"],
        "personel_fiyati": ilk["personel_fiyati"],
        "rezervasyon_son": ilk["rezervasyon_son"].isoformat(),
        "yemekler": yemekler,
        "toplam_kalori": sum(y["kalori"] for y in yemekler),
        "tamami_vejetaryen": all(y["vejetaryen"] for y in yemekler),
    }


def menu_doluluk(menu_id, taze=False):
    """Boş yer sayısı ve son saat bilgisi (sık değişir)."""
    with baglanti.okuma_baglantisi(taze) as b:
        satir = baglanti.tek_satir(
            b,
            """SELECT kapasite, rezerve, bos_yer, doluluk_yuzde,
                      (NOW() >= rezervasyon_son) AS suresi_doldu
                 FROM v_menu_doluluk WHERE menu_id = %s""",
            (menu_id,),
        )
    if satir:
        satir["suresi_doldu"] = bool(satir["suresi_doldu"])
    return satir

def haftalik(yemekhane_id, baslangic, kullanici_id, taze=False):
    """Başlangıç gününden itibaren 7 günün menüleri; boş yer ve kullanıcının rezervasyon durumuyla."""
    with baglanti.okuma_baglantisi(taze) as b:
        satirlar = baglanti.sorgula(
            b,
            """SELECT d.menu_id, d.tarih, d.ogun_id, d.ogun,
                      d.kapasite, d.rezerve, d.bos_yer, d.rezervasyon_son,
                      (NOW() >= d.rezervasyon_son) AS suresi_doldu,
                      m.ogrenci_fiyati, m.personel_fiyati,
                      r.id AS rezervasyon_id, r.durum AS rezervasyon_durumu,
                      (SELECT GROUP_CONCAT(y.ad ORDER BY k.sira, y.ad SEPARATOR ', ')
                         FROM menu_yemekleri my
                         JOIN yemekler y           ON y.id = my.yemek_id
                         JOIN yemek_kategorileri k ON k.id = y.kategori_id
                        WHERE my.menu_id = d.menu_id) AS yemekler
                 FROM v_menu_doluluk d
                 JOIN menuler m ON m.id = d.menu_id
                 LEFT JOIN rezervasyonlar r
                        ON r.menu_id = d.menu_id AND r.kullanici_id = %s
                WHERE d.yemekhane_id = %s
                  AND d.tarih BETWEEN %s AND DATE_ADD(%s, INTERVAL 6 DAY)
                ORDER BY d.tarih, d.ogun_id""",
            (kullanici_id, yemekhane_id, baslangic, baslangic),
        )
    for s in satirlar:
        s["suresi_doldu"] = bool(s["suresi_doldu"])
    return satirlar