class IsKuraliHatasi(Exception):
    """Kural ihlali ya da geçersiz girdi (HTTP 400). Mesaj kullanıcıya olduğu gibi iletilir."""


class BulunamadiHatasi(IsKuraliHatasi):
    """İstenen kayıt yok (HTTP 404)."""


class YetkiHatasi(IsKuraliHatasi):
    """Kimlik doğrulanamadı (HTTP 401)."""