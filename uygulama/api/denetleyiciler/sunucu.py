from django.http import JsonResponse

from ..veri import sunucu_repo


def bilgi(istek):
    return JsonResponse(sunucu_repo.bilgi())