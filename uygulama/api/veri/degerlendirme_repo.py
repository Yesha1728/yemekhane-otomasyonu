import pymysql

from . import baglanti
from .hatalar import IsKuraliHatasi


def kullanilan_menuler(kullanici_id, taze=False):
    """Kullanıcının 'kullanildi' durumundaki rezervasyonları ve varsa verdiği oy."""
    with baglanti.okuma_baglantisi(taze) as b:
        return baglanti.sorgula(
            b,
            """SELECT r.menu_id, m.tarih, yh.ad AS yemekhane, o.ad AS ogun, d.puan, d.yorum
                 FROM rezervasyonlar r
                 JOIN menuler m       ON m.id  = r.menu_id
                 JOIN yemekhaneler yh ON yh.id = m.yemekhane_id
                 JOIN ogunler o       ON o.id  = m.ogun_id
                 LEFT JOIN degerlendirmeler d
                        ON d.menu_id = r.menu_id AND d.kullanici_id = r.kullanici_id
                WHERE r.kullanici_id = %s AND r.durum = 'kullanildi'
                ORDER BY m.tarih DESC, o.sira DESC""",
            (kullanici_id,),
        )


def menu_kullanildi_mi(kullanici_id, menu_id):
    """Kural kontrolü için KAYNAKTAN okunur (replika gecikmesine güvenilmez)."""
    with baglanti.yazma_baglantisi() as b:
        satir = baglanti.tek_satir(
            b,
            "SELECT 1 AS var FROM rezervasyonlar WHERE kullanici_id = %s AND menu_id = %s AND durum = 'kullanildi'",
            (kullanici_id, menu_id),
        )
    return satir is not None


def ekle(kullanici_id, menu_id, puan, yorum):
    with baglanti.yazma_baglantisi() as b:
        try:
            with b.cursor() as imlec:
                imlec.execute(
                    "INSERT INTO degerlendirmeler (kullanici_id, menu_id, puan, yorum) VALUES (%s, %s, %s, %s)",
                    (kullanici_id, menu_id, puan, yorum),
                )
        except pymysql.err.IntegrityError as hata:
            if hata.args[0] == 1062:        # uq_degerlendirme: kişi başına menü başına tek oy
                raise IsKuraliHatasi("Bu menüyü zaten değerlendirdiniz.") from None
            raise