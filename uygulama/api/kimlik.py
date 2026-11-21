import bcrypt


def sifre_dogru_mu(sifre, hash_degeri):
    """Düz şifreyi veritabanındaki bcrypt özetiyle karşılaştırır."""
    try:
        return bcrypt.checkpw(sifre.encode("utf-8"), hash_degeri.encode("utf-8"))
    except ValueError:
        return False