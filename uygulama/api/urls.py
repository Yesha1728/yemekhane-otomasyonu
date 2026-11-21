from django.urls import path

from .denetleyiciler import kimlik, sunucu

urlpatterns = [
    path("", kimlik.kok),
    path("giris", kimlik.giris),
    path("cikis", kimlik.cikis),
    path("ben", kimlik.ben),
    path("sunucular", sunucu.bilgi),
]