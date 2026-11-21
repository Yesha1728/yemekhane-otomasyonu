from ..ortak import govde, tamsayi, uc_nokta, yanit
from ..veri import kullanici_repo, rezervasyon_repo


@uc_nokta("POST")
def yap(istek):
    menu_id = tamsayi(govde(istek).get("menu_id"), "menu_id")
    # Kullanıcı numarası istekten değil, oturumdan alınır: kimse başkası adına rezervasyon yapamaz.
    sonuc = rezervasyon_repo.yap(istek.kullanici["id"], menu_id)          # sp_rezervasyon_yap (kaynak)
    # Gösterilecek bakiye KAYNAKTAN okunur: replika henüz yeni bakiyeyi almamış olabilir.
    bakiye = kullanici_repo.bakiye_getir(istek.kullanici["id"], taze=True)
    return yanit({
        "rezervasyon_id": sonuc["rezervasyon_id"],
        "ucret": sonuc["ucret"],
        "bakiye": bakiye,
    }, 201)