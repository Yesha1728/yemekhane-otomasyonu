from django.urls import path

from .denetleyiciler import kimlik, sunucu

urlpatterns = [
    path("", kimlik.kok),
    path("sunucular", sunucu.bilgi),
]