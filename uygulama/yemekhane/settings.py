import os

SECRET_KEY = os.environ.get("SECRET_KEY", "ders-ortami-icin-gizli-anahtar")
DEBUG = False
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = []
MIDDLEWARE = []
DATABASES = {}

ROOT_URLCONF = "yemekhane.urls"
WSGI_APPLICATION = "yemekhane.wsgi.application"

LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_TZ = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"basit": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
    "handlers": {"konsol": {"class": "logging.StreamHandler", "formatter": "basit"}},
    "root": {"handlers": ["konsol"], "level": "INFO"},
}