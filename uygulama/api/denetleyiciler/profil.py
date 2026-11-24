from .. import is_kurallari
from ..ortak import govde, taze_mi, uc_nokta, yanit
from ..veri import kullanici_repo
from ..veri.hatalar import IsKuraliHatasi


@uc_nokta(("GET", "POST"))
def alerjenler(istek):
    """GET: tüm alerjenler, kullanıcının seçtikleri işaretli. POST: seçimi kaydeder (yazma: kaynak)."""
    kullanici_id = istek.kullanici["id"]
    if istek.method == "POST":
        secilen = govde(istek).get("alerjen_idler")
        if not isinstance(secilen, list):
            raise IsKuraliHatasi("alerjen_idler bir liste olmalı.")
        gecerli = {a["id"] for a in kullanici_repo.alerjen_listesi(taze=True)}
        kullanici_repo.alerjenleri_kaydet(kullanici_id, is_kurallari.alerjen_secimi_temizle(secilen, gecerli))
        taze = True          # yazmadan sonra kaynaktan oku (replika geride kalabilir)
    else:
        taze = taze_mi(istek)

    secili = set(kullanici_repo.alerjenleri_getir(kullanici_id, taze))
    liste = [{"id": a["id"], "ad": a["ad"], "secili": a["id"] in secili}
             for a in kullanici_repo.alerjen_listesi(taze)]
    return yanit({"alerjenler": liste})