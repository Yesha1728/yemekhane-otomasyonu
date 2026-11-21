from django.urls import path

from .denetleyiciler import kimlik

urlpatterns = [
    path("", kimlik.kok),
]