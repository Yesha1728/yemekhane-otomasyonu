from . import baglanti


def yap(kullanici_id, menu_id):
    """sp_rezervasyon_yap · yazma (kaynak). Döner: rezervasyon_id, ucret, bakiye"""
    with baglanti.yazma_baglantisi() as b:
        return baglanti.yordam_cagir(b, "sp_rezervasyon_yap", kullanici_id, menu_id)