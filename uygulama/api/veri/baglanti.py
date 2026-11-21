import os
from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor

YAZMA_HOST = os.environ.get("DB_YAZMA_HOST", "mysql-primary")
OKUMA_HOST = os.environ.get("DB_OKUMA_HOST", "mysql-replica")


def _bagla(host):
    return pymysql.connect(
        host=host,
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_KULLANICI", "yemekhane_app"),
        password=os.environ.get("DB_SIFRE", "Uyg_2026"),
        database=os.environ.get("DB_ADI", "yemekhane"),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
        connect_timeout=5,
        read_timeout=15,
    )


@contextmanager
def yazma_baglantisi():
    baglanti = _bagla(YAZMA_HOST)
    try:
        yield baglanti
    finally:
        baglanti.close()


@contextmanager
def okuma_baglantisi(taze=False):
    """Replikaya bağlantı. taze=True ise (yazmadan hemen sonra okuma) kaynağa bağlanır."""
    baglanti = _bagla(YAZMA_HOST if taze else OKUMA_HOST)
    try:
        yield baglanti
    finally:
        baglanti.close()


def sorgula(baglanti, sql, parametreler=()):
    with baglanti.cursor() as imlec:
        imlec.execute(sql, parametreler)
        return list(imlec.fetchall())


def tek_satir(baglanti, sql, parametreler=()):
    with baglanti.cursor() as imlec:
        imlec.execute(sql, parametreler)
        return imlec.fetchone()