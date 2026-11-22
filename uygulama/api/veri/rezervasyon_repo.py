from . import baglanti


def yap(kullanici_id, menu_id):
    """sp_rezervasyon_yap · yazma (kaynak). Döner: rezervasyon_id, ucret, bakiye"""
    with baglanti.yazma_baglantisi() as b:
        return baglanti.yordam_cagir(b, "sp_rezervasyon_yap", kullanici_id, menu_id)


def iptal(kullanici_id, rezervasyon_id):
    """sp_rezervasyon_iptal · yazma (kaynak). Döner: rezervasyon_id, iade, bakiye"""
    with baglanti.yazma_baglantisi() as b:
        return baglanti.yordam_cagir(b, "sp_rezervasyon_iptal", kullanici_id, rezervasyon_id)


def turnike_gecis(kullanici_id, yemekhane_id, zaman):
    """sp_turnike_gecis · yazma (kaynak). zaman None ise şu an. Döner: rezervasyon_id, menu_id, ogun"""
    with baglanti.yazma_baglantisi() as b:
        return baglanti.yordam_cagir(b, "sp_turnike_gecis", kullanici_id, yemekhane_id, zaman)


def listele(kullanici_id, taze=False):
    """Kullanıcının rezervasyonları (en yeni önce). Listeleme: replika."""
    with baglanti.okuma_baglantisi(taze) as b:
        satirlar = baglanti.sorgula(
            b,
            """SELECT r.id AS rezervasyon_id, r.menu_id, r.durum, r.ucret,
                      r.olusturma, r.kullanma_zamani, r.iptal_zamani,
                      m.tarih, yh.ad AS yemekhane, o.ad AS ogun,
                      TIMESTAMP(m.tarih, o.son_saat)             AS rezervasyon_son,
                      (NOW() >= TIMESTAMP(m.tarih, o.son_saat))  AS suresi_doldu
                 FROM rezervasyonlar r
                 JOIN menuler m       ON m.id  = r.menu_id
                 JOIN yemekhaneler yh ON yh.id = m.yemekhane_id
                 JOIN ogunler o       ON o.id  = m.ogun_id
                WHERE r.kullanici_id = %s
                ORDER BY m.tarih DESC, o.sira DESC
                LIMIT 100""",
            (kullanici_id,),
        )
    for s in satirlar:
        s["suresi_doldu"] = bool(s["suresi_doldu"])
    return satirlar