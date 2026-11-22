from ..ortak import govde, taze_mi, tamsayi, uc_nokta, yanit
from ..veri import degerlendirme_repo
from ..veri.hatalar import IsKuraliHatasi


@uc_nokta("GET")
def liste(istek):
    return yanit({"menuler": degerlendirme_repo.kullanilan_menuler(istek.kullanici["id"], taze_mi(istek))})


@uc_nokta("POST")
def ekle(istek):
    veri = govde(istek)
    menu_id = tamsayi(veri.get("menu_id"), "menu_id")
    puan = tamsayi(veri.get("puan"), "puan")
    yorum = str(veri.get("yorum") or "").strip()

    if not 1 <= puan <= 5:
        raise IsKuraliHatasi("Puan 1 ile 5 arasında olmalıdır.")
    if len(yorum) > 500:
        raise IsKuraliHatasi("Yorum en fazla 500 karakter olabilir.")

    # Uygulama kuralı: yalnızca kullanılmış menü değerlendirilebilir.
    if not degerlendirme_repo.menu_kullanildi_mi(istek.kullanici["id"], menu_id):
        raise IsKuraliHatasi("Yalnızca kullandığınız (turnikeden geçtiğiniz) menüyü değerlendirebilirsiniz.")

    degerlendirme_repo.ekle(istek.kullanici["id"], menu_id, puan, yorum or None)
    return yanit({"tamam": True}, 201)