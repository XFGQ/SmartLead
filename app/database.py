# app/database.py - Dijital Coban SmartLead AI
# Modul B: SQL SADECE burada. HTTP ve yapay zeka bilmez.
import os
import sqlite3

from flask import current_app, g

SEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    isim          TEXT    NOT NULL,
    telefon       TEXT    NOT NULL,
    hayvan_sayisi INTEGER,
    mesaj         TEXT,
    tarih         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    """Istek basina tek baglanti acar ve istek bitince kapatir."""
    if "db" not in g:
        yol = current_app.config["DATABASE_URL"]
        klasor = os.path.dirname(yol)
        if klasor:
            os.makedirs(klasor, exist_ok=True)
        g.db = sqlite3.connect(yol)
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
        get_db().executescript(SEMA)
        get_db().commit()


def lead_ekle(isim, telefon, hayvan_sayisi=None, mesaj=None):
    """Yeni lead kaydeder, kaydin id'sini dondurur. Tum degerler ? ile parametreli."""
    db = get_db()
    imlec = db.execute(
        "INSERT INTO leads (isim, telefon, hayvan_sayisi, mesaj) VALUES (?, ?, ?, ?)",
        (isim, telefon, hayvan_sayisi, mesaj),
    )
    db.commit()
    return imlec.lastrowid


def tum_leadler():
    """Tum lead'leri en yeniden eskiye sozluk listesi olarak dondurur."""
    satirlar = get_db().execute(
        "SELECT id, isim, telefon, hayvan_sayisi, mesaj, tarih FROM leads ORDER BY tarih DESC, id DESC"
    ).fetchall()
    return [dict(s) for s in satirlar]
