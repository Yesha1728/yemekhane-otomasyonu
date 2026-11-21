from django.http import JsonResponse


def kok(istek):
    return JsonResponse({"uygulama": "Yemekhane Otomasyonu API", "durum": "calisiyor"})