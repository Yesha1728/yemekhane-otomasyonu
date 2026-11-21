from django.urls import path

from .denetleyiciler import kimlik, menu, rezervasyon, sunucu

urlpatterns = [
    path("", kimlik.kok),
    path("giris", kimlik.giris),
    path("cikis", kimlik.cikis),
    path("ben", kimlik.ben),
    path("sunucular", sunucu.bilgi),
    path("secenekler", menu.secenekler),
    path("menu/gunluk", menu.gunluk),
    path("menu/haftalik", menu.haftalik),
    path("rezervasyon", rezervasyon.yap),
    path("rezervasyon/<int:rezervasyon_id>/iptal", rezervasyon.iptal),
    path("rezervasyonlarim", rezervasyon.listele),
]