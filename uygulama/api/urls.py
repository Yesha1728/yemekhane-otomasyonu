from django.urls import path

from .denetleyiciler import bakiye, degerlendirme, kimlik, menu, profil, rezervasyon, sunucu, yonetici

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
    path("bakiye", bakiye.goster),
    path("bakiye/yukle", bakiye.yukle),
    path("degerlendirme", degerlendirme.liste),
    path("degerlendirme/ekle", degerlendirme.ekle),
    path("profil/alerjenler", profil.alerjenler),
    path("yonetici/menuler", yonetici.liste),
    path("yonetici/yemekler", yonetici.yemekler),
    path("yonetici/menu", yonetici.olustur),
    path("yonetici/menu/<int:menu_id>", yonetici.detay_veya_guncelle),
    path("yonetici/turnike", yonetici.turnike),
]