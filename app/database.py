# app/database.py - Dijital Coban SmartLead AI
# Modul B: SQL SADECE burada. HTTP ve yapay zeka bilmez.
# DATABASE_URL "postgres://" veya "postgresql://" ile basliyorsa PostgreSQL (kalici),
# aksi halde dosya yolu kabul edilir ve SQLite kullanilir (yerel gelistirme).
import os
import sqlite3

from flask import current_app, g

SEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS leads (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    isim          TEXT    NOT NULL,
    telefon       TEXT    NOT NULL,
    hayvan_sayisi INTEGER,
    mesaj         TEXT,
    tarih         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

SEMA_POSTGRES = """
CREATE TABLE IF NOT EXISTS leads (
    id            SERIAL PRIMARY KEY,
    isim          TEXT    NOT NULL,
    telefon       TEXT    NOT NULL,
    hayvan_sayisi INTEGER,
    mesaj         TEXT,
    tarih         TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'UTC')
);
"""


def postgres_mu():
    return current_app.config["DATABASE_URL"].startswith(("postgres://", "postgresql://"))


def _sql(sorgu):
    """Sorgular ? yer tutucusuyla yazilir; PostgreSQL icin %s'ye cevrilir."""
    return sorgu.replace("?", "%s") if postgres_mu() else sorgu


def get_db():
    """Istek basina tek baglanti acar ve istek bitince kapatir."""
    if "db" not in g:
        url = current_app.config["DATABASE_URL"]
        if postgres_mu():
            import psycopg
            from psycopg.rows import dict_row
            g.db = psycopg.connect(url, row_factory=dict_row, connect_timeout=15)
        else:
            klasor = os.path.dirname(url)
            if klasor:
                os.makedirs(klasor, exist_ok=True)
            g.db = sqlite3.connect(url)
            g.db.row_factory = sqlite3.Row
    return g.db


def _baglanti_kapat(_hata=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Tablo yoksa olusturur ve baglanti kapatma kancasini kaydeder."""
    app.teardown_appcontext(_baglanti_kapat)
    with app.app_context():
        db = get_db()
        if postgres_mu():
            db.execute(SEMA_POSTGRES)
        else:
            db.executescript(SEMA_SQLITE)
        db.commit()


def lead_ekle(isim, telefon, hayvan_sayisi=None, mesaj=None):
    """Yeni lead kaydeder, kaydin id'sini dondurur. Tum degerler parametreli (SQL Injection korumasi)."""
    db = get_db()
    imlec = db.execute(
        _sql("INSERT INTO leads (isim, telefon, hayvan_sayisi, mesaj) VALUES (?, ?, ?, ?) RETURNING id"),
        (isim, telefon, hayvan_sayisi, mesaj),
    )
    lead_id = imlec.fetchone()["id"]
    db.commit()
    return lead_id


def tum_leadler():
    """Tum lead'leri en yeniden eskiye sozluk listesi olarak dondurur. Tarih: 'YYYY-MM-DD HH:MM:SS' (UTC)."""
    tarih = "to_char(tarih, 'YYYY-MM-DD HH24:MI:SS')" if postgres_mu() else "tarih"
    satirlar = get_db().execute(
        f"SELECT id, isim, telefon, hayvan_sayisi, mesaj, {tarih} AS tarih FROM leads ORDER BY leads.tarih DESC, id DESC"
    ).fetchall()
    return [dict(s) for s in satirlar]
