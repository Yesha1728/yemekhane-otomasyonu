import bcrypt

from . import oturum


def sifre_dogru_mu(sifre, hash_degeri):
    """Düz şifreyi veritabanındaki bcrypt özetiyle karşılaştırır."""
    try:
        return bcrypt.checkpw(sifre.encode("utf-8"), hash_degeri.encode("utf-8"))
    except ValueError:
        return False


def jeton_oku(istek):
    """'Authorization: Bearer <jeton>' başlığından jetonu çıkarır."""
    baslik = istek.headers.get("Authorization", "")
    if baslik.startswith("Bearer "):
        return baslik[7:].strip()
    return None


def istekten_kullanici(istek):
    """İsteği yapan kullanıcıyı verir (süreyi de yeniler); oturum yoksa None."""
    return oturum.getir(jeton_oku(istek))