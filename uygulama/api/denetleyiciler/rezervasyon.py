from .. import is_kurallari
from ..ortak import govde, taze_mi, tamsayi, uc_nokta, yanit
from ..veri import kullanici_repo, rezervasyon_repo


@uc_nokta("POST")
def yap(istek):
    veri = govde(istek)
    menu_id = tamsayi(veri.get("menu_id"), "menu_id")
    # Porsiyon seçilmediyse tam porsiyon. Geçerli olup olmadığını ve öğüne uyup uymadığını yordam denetler.
    porsiyon = str(veri.get("porsiyon") or "tam").strip().lower()
    # Kullanıcı numarası istekten değil, oturumdan alınır: kimse başkası adına rezervasyon yapamaz.
    sonuc = rezervasyon_repo.yap(istek.kullanici["id"], menu_id, porsiyon)   # sp_rezervasyon_yap (kaynak)
    # Gösterilecek bakiye KAYNAKTAN okunur: replika henüz yeni bakiyeyi almamış olabilir.
    bakiye = kullanici_repo.bakiye_getir(istek.kullanici["id"], taze=True)
    return yanit({
        "rezervasyon_id": sonuc["rezervasyon_id"],
        "ucret": sonuc["ucret"],
        "porsiyon": sonuc["porsiyon"],
        "bakiye": bakiye,
    }, 201)


@uc_nokta("POST")
def iptal(istek, rezervasyon_id):
    sonuc = rezervasyon_repo.iptal(istek.kullanici["id"], rezervasyon_id)  # sp_rezervasyon_iptal (kaynak)
    bakiye = kullanici_repo.bakiye_getir(istek.kullanici["id"], taze=True)
    return yanit({
        "rezervasyon_id": sonuc["rezervasyon_id"],
        "iade": sonuc["iade"],
        "bakiye": bakiye,
    })


@uc_nokta("GET")
def listele(istek):
    satirlar = rezervasyon_repo.listele(istek.kullanici["id"], taze_mi(istek))
    for s in satirlar:
        s["iptal_edilebilir"] = is_kurallari.iptal_edilebilir(s["durum"], s["suresi_doldu"])
    return yanit({"rezervasyonlar": satirlar})