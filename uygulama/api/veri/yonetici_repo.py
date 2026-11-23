import pymysql

from . import baglanti, menu_onbellek
from .hatalar import BulunamadiHatasi, IsKuraliHatasi


def menu_listesi(baslangic, bitis, yemekhane_id=None, taze=False):
    """Menü bazında doluluk ve ortalama puan (rapor: replika)."""
    sql = """SELECT d.menu_id, d.tarih, d.yemekhane_id, d.yemekhane, d.ogun_id, d.ogun,
                    d.kapasite, d.rezerve, d.bos_yer, d.doluluk_yuzde,
                    p.oy_sayisi, p.ortalama_puan, m.ogrenci_fiyati, m.personel_fiyati
               FROM v_menu_doluluk d
               JOIN v_menu_puan p ON p.menu_id = d.menu_id
               JOIN menuler m     ON m.id = d.menu_id
              WHERE d.tarih BETWEEN %s AND %s"""
    parametreler = [baslangic, bitis]
    if yemekhane_id is not None:
        sql += " AND d.yemekhane_id = %s"
        parametreler.append(yemekhane_id)
    sql += " ORDER BY d.tarih DESC, d.yemekhane_id, d.ogun_id"
    with baglanti.okuma_baglantisi(taze) as b:
        return baglanti.sorgula(b, sql, parametreler)


def yemek_katalogu(taze=False):
    """Menüye konabilecek tüm yemekler (kategori sırasıyla)."""
    with baglanti.okuma_baglantisi(taze) as b:
        satirlar = baglanti.sorgula(
            b,
            """SELECT y.id AS yemek_id, y.ad AS yemek, y.kalori, y.vejetaryen,
                      k.ad AS kategori, k.sira AS kategori_sira
                 FROM yemekler y
                 JOIN yemek_kategorileri k ON k.id = y.kategori_id
                ORDER BY k.sira, y.ad""",
        )
    for s in satirlar:
        s["vejetaryen"] = bool(s["vejetaryen"])
    return satirlar


def duzenleme_detayi(menu_id):
    """Düzenlenecek menü: eski veriyle düzenleme yapılmasın diye KAYNAKTAN okunur."""
    with baglanti.yazma_baglantisi() as b:
        menu = baglanti.tek_satir(
            b,
            """SELECT id AS menu_id, yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati
                 FROM menuler WHERE id = %s""",
            (menu_id,),
        )
        if menu is None:
            return None
        yemekler = baglanti.sorgula(b, "SELECT yemek_id FROM menu_yemekleri WHERE menu_id = %s", (menu_id,))
    menu["tarih"] = menu["tarih"].isoformat()
    menu["yemek_idleri"] = [y["yemek_id"] for y in yemekler]
    return menu


def menu_olustur(yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati, yemek_idleri):
    """Yeni menü + yemekleri tek transaction'da, kaynağa yazılır. Döner: menu_id"""
    with baglanti.yazma_baglantisi() as b:
        b.begin()
        try:
            with b.cursor() as imlec:
                imlec.execute(
                    """INSERT INTO menuler (yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati),
                )
                menu_id = imlec.lastrowid
                imlec.executemany(
                    "INSERT INTO menu_yemekleri (menu_id, yemek_id) VALUES (%s, %s)",
                    [(menu_id, y) for y in yemek_idleri],
                )
            b.commit()
            return menu_id
        except pymysql.err.IntegrityError as hata:
            b.rollback()
            if hata.args[0] == 1062:      # uq_menu: yemekhane + tarih + öğün başına tek menü
                raise IsKuraliHatasi("Bu yemekhane, tarih ve öğün için zaten bir menü var.") from None
            if hata.args[0] == 1452:      # yabancı anahtar
                raise IsKuraliHatasi("Seçilen yemekhane, öğün ya da yemek geçerli değil.") from None
            raise
        except Exception:
            b.rollback()
            raise


def menu_guncelle(menu_id, ogrenci_fiyati, personel_fiyati, yemek_idleri):
    """
    Menünün fiyatlarını ve yemeklerini değiştirir (kaynağa, tek transaction).
    Yemekhane, tarih ve öğün değiştirilemez. Döner: menünün anahtarı (yemekhane_id, tarih, ogun_id);
    Aşama 3'te önbellek bu anahtarla temizlenecek.
    """
    with baglanti.yazma_baglantisi() as b:
        b.begin()
        try:
            with b.cursor() as imlec:
                imlec.execute(
                    "SELECT yemekhane_id, tarih, ogun_id FROM menuler WHERE id = %s FOR UPDATE",
                    (menu_id,),
                )
                menu = imlec.fetchone()
                if menu is None:
                    b.rollback()
                    raise BulunamadiHatasi("Menü bulunamadı.")
                imlec.execute(
                    "UPDATE menuler SET ogrenci_fiyati = %s, personel_fiyati = %s WHERE id = %s",
                    (ogrenci_fiyati, personel_fiyati, menu_id),
                )
                imlec.execute("DELETE FROM menu_yemekleri WHERE menu_id = %s", (menu_id,))
                imlec.executemany(
                    "INSERT INTO menu_yemekleri (menu_id, yemek_id) VALUES (%s, %s)",
                    [(menu_id, y) for y in yemek_idleri],
                )
            b.commit()
        except pymysql.err.IntegrityError as hata:
            b.rollback()
            if hata.args[0] == 1452:
                raise IsKuraliHatasi("Seçilen yemek geçerli değil.") from None
            raise
        except BulunamadiHatasi:
            raise
        except Exception:
            b.rollback()
            raise
        
    menu["tarih"] = menu["tarih"].isoformat()
    menu_onbellek.sil(menu["yemekhane_id"], menu["tarih"], menu["ogun_id"])
    return menu