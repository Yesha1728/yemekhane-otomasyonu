from decimal import Decimal, InvalidOperation

from ..ortak import govde, taze_mi, uc_nokta, yanit
from ..veri import kullanici_repo
from ..veri.hatalar import IsKuraliHatasi


@uc_nokta("GET")
def goster(istek):
    taze = taze_mi(istek)
    kimlik_no = istek.kullanici["id"]
    return yanit({
        "bakiye": kullanici_repo.bakiye_getir(kimlik_no, taze),
        "hareketler": kullanici_repo.bakiye_hareketleri(kimlik_no, taze),
    })


@uc_nokta("POST")
def yukle(istek):
    ham = govde(istek).get("tutar")
    try:
        tutar = Decimal(str(ham)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise IsKuraliHatasi("Yükleme tutarı bir sayı olmalıdır.") from None
    if not tutar.is_finite():
        raise IsKuraliHatasi("Yükleme tutarı bir sayı olmalıdır.")
    # Tutar aralığını (10-1000 TL) yordam denetler; mesajı olduğu gibi arayüze gider.
    sonuc = kullanici_repo.bakiye_yukle(istek.kullanici["id"], tutar)     # sp_bakiye_yukle (kaynak)
    return yanit({"hareket_id": sonuc["hareket_id"], "bakiye": sonuc["bakiye"]}, 201)