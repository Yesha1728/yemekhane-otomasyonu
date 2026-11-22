import datetime
from decimal import Decimal, InvalidOperation

from ..ortak import govde, tamsayi, tarih, taze_mi, uc_nokta, yanit
from ..veri import menu_repo, rezervasyon_repo, yonetici_repo
from ..veri.hatalar import BulunamadiHatasi, IsKuraliHatasi

YONETICI = ("yonetici",)


def _fiyat(deger, ad):
    try:
        fiyat = Decimal(str(deger)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise IsKuraliHatasi(f"{ad} bir sayı olmalıdır.") from None
    if not fiyat.is_finite() or fiyat < 0 or fiyat > 9999:
        raise IsKuraliHatasi(f"{ad} 0 ile 9999 arasında olmalıdır.")
    return fiyat


def _yemek_idleri(deger):
    if not isinstance(deger, list) or not deger:
        raise IsKuraliHatasi("Menüde en az bir yemek seçilmelidir.")
    return sorted({tamsayi(x, "yemek_id") for x in deger})


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


@uc_nokta("POST", roller=YONETICI)
def olustur(istek):
    veri = govde(istek)
    menu_id = yonetici_repo.menu_olustur(
        tamsayi(veri.get("yemekhane_id"), "yemekhane_id"),
        tarih(veri.get("tarih"), "tarih"),
        tamsayi(veri.get("ogun_id"), "ogun_id"),
        _fiyat(veri.get("ogrenci_fiyati"), "Öğrenci fiyatı"),
        _fiyat(veri.get("personel_fiyati"), "Personel fiyatı"),
        _yemek_idleri(veri.get("yemek_idleri")),
    )
    return yanit({"menu_id": menu_id}, 201)


@uc_nokta(("GET", "PUT"), roller=YONETICI)
def detay_veya_guncelle(istek, menu_id):
    if istek.method == "GET":
        menu = yonetici_repo.duzenleme_detayi(menu_id)
        if menu is None:
            raise BulunamadiHatasi("Menü bulunamadı.")
        return yanit(menu)

    veri = govde(istek)
    yonetici_repo.menu_guncelle(
        menu_id,
        _fiyat(veri.get("ogrenci_fiyati"), "Öğrenci fiyatı"),
        _fiyat(veri.get("personel_fiyati"), "Personel fiyatı"),
        _yemek_idleri(veri.get("yemek_idleri")),
    )
    return yanit({"tamam": True})


@uc_nokta("POST", roller=YONETICI)
def turnike(istek):
    """Turnike geçişini taklit eder (sp_turnike_gecis). Test ve gösterim içindir."""
    veri = govde(istek)
    kullanici_id = tamsayi(veri.get("kullanici_id"), "kullanici_id")
    yemekhane_id = tamsayi(veri.get("yemekhane_id"), "yemekhane_id")
    ham_zaman = str(veri.get("zaman") or "").strip()
    zaman = None
    if ham_zaman:
        try:
            zaman = datetime.datetime.fromisoformat(ham_zaman).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise IsKuraliHatasi("Zaman YYYY-AA-GG SS:DD biçiminde olmalıdır.") from None
    return yanit(rezervasyon_repo.turnike_gecis(kullanici_id, yemekhane_id, zaman))