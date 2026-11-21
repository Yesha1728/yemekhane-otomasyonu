from ..ortak import uc_nokta, yanit
from ..veri import sunucu_repo


@uc_nokta("GET")
def bilgi(istek):
    return yanit(sunucu_repo.bilgi())