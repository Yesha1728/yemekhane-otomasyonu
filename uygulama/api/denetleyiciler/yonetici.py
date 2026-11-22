import datetime

from ..ortak import tamsayi, tarih, taze_mi, uc_nokta, yanit
from ..veri import menu_repo, yonetici_repo
from ..veri.hatalar import BulunamadiHatasi

YONETICI = ("yonetici",)


@uc_nokta("GET", roller=YONETICI)
def liste(istek):
    taze = taze_mi(istek)
    bugun = menu_repo.bugun(taze)
    baslangic = tarih(istek.GET.get("baslangic"), "baslangic", varsayilan=bugun - datetime.timedelta(days=7))
    bitis = tarih(istek.GET.get("bitis"), "bitis", varsayilan=bugun + datetime.timedelta(days=14))
    ham_yemekhane = istek.GET.get("yemekhane_id")
    yemekhane_id = tamsayi(ham_yemekhane, "yemekhane_id") if ham_yemekhane else None
    return yanit({"menuler": yonetici_repo.menu_listesi(baslangic, bitis, yemekhane_id, taze)})


@uc_nokta("GET", roller=YONETICI)
def yemekler(istek):
    return yanit({"yemekler": yonetici_repo.yemek_katalogu()})


@uc_nokta("GET", roller=YONETICI)
def detay(istek, menu_id):
    menu = yonetici_repo.duzenleme_detayi(menu_id)
    if menu is None:
        raise BulunamadiHatasi("Menü bulunamadı.")
    return yanit(menu)