from .. import is_kurallari
from ..ortak import tamsayi, tarih, taze_mi, uc_nokta, yanit
from ..veri import menu_repo
from ..veri.hatalar import BulunamadiHatasi


@uc_nokta("GET")
def secenekler(istek):
    """Seçim kutuları için yemekhane ve öğün listesi, bir de bugünün tarihi."""
    taze = taze_mi(istek)
    return yanit({
        "yemekhaneler": menu_repo.yemekhaneler(taze),
        "ogunler": menu_repo.ogunler(taze),
        "bugun": menu_repo.bugun(taze),
    })


@uc_nokta("GET")
def gunluk(istek):
    """Bir yemekhanenin bir günkü bir öğün menüsü."""
    taze = taze_mi(istek)
    yemekhane_id = tamsayi(istek.GET.get("yemekhane_id"), "yemekhane_id", varsayilan=1)
    ogun_id = tamsayi(istek.GET.get("ogun_id"), "ogun_id", varsayilan=2)
    gun = tarih(istek.GET.get("tarih"), "tarih", varsayilan=menu_repo.bugun(taze))

    menu = menu_repo.menu_icerik(yemekhane_id, gun, ogun_id, taze)
    if menu is None:
        raise BulunamadiHatasi("Bu yemekhane, tarih ve öğün için menü bulunamadı.")

    doluluk = menu_repo.menu_doluluk(menu["menu_id"], taze)
    sonuc = dict(menu)
    sonuc["fiyat"] = is_kurallari.kullanici_fiyati(
        istek.kullanici["rol"], menu["ogrenci_fiyati"], menu["personel_fiyati"])
    sonuc.update({
        "kapasite": doluluk["kapasite"],
        "bos_yer": doluluk["bos_yer"],
        "suresi_doldu": doluluk["suresi_doldu"],
    })
    return yanit(sonuc)