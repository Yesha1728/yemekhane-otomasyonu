from .. import kimlik, oturum
from ..ortak import govde, uc_nokta, yanit
from ..veri import kullanici_repo
from ..veri.hatalar import IsKuraliHatasi, YetkiHatasi


@uc_nokta("GET")
def kok(istek):
    return yanit({"uygulama": "Yemekhane Otomasyonu API", "durum": "calisiyor"})


@uc_nokta("POST")
def giris(istek):
    veri = govde(istek)
    eposta = str(veri.get("eposta", "")).strip().lower()
    sifre = str(veri.get("sifre", ""))
    if not eposta or not sifre:
        raise IsKuraliHatasi("E-posta ve şifre gerekli.")

    kayit = kullanici_repo.eposta_ile_bul(eposta)
    # Kullanıcı yoksa da yanlış şifreyle aynı mesaj verilir (hesap var mı sızdırılmaz).
    if kayit is None or not kimlik.sifre_dogru_mu(sifre, kayit["sifre_hash"]):
        raise YetkiHatasi("E-posta ya da şifre hatalı.")
    if not kayit["aktif"]:
        raise YetkiHatasi("Hesabınız pasif durumda.")

    kullanici = {k: kayit[k] for k in ("id", "ad", "soyad", "eposta", "rol")}
    jeton = oturum.olustur(kullanici)
    return yanit({"jeton": jeton, "kullanici": kullanici})