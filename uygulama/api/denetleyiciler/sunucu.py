from ..ortak import uc_nokta, yanit
from ..veri import sunucu_repo


@uc_nokta("GET", giris=False)
def bilgi(istek):
    return yanit(sunucu_repo.bilgi())