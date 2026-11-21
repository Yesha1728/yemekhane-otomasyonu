from . import baglanti

SORGU = "SELECT @@server_id AS sunucu_no, @@super_read_only AS salt_okunur"


def bilgi():
    with baglanti.yazma_baglantisi() as b:
        yazma = baglanti.tek_satir(b, SORGU)
    with baglanti.okuma_baglantisi() as b:
        okuma = baglanti.tek_satir(b, SORGU)
    return {"yazma": yazma, "okuma": okuma}