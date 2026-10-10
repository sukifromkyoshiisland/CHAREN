import sqlite3
from flask import current_app


def get_db():
    # Veritabanına bağlan
    connection = sqlite3.connect("charen.db")
    connection.row_factory = sqlite3.Row
    return connection


def init_db(app):
    # Tablo yoksa oluştur
    with app.app_context():
        with get_db() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isim TEXT NOT NULL,
                    telefon TEXT NOT NULL,
                    mesaj TEXT,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


def lead_ekle(isim, telefon, mesaj=""):
    # Ziyaretçinin bilgilerini güvenli şekilde kaydet
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO leads (isim, telefon, mesaj) VALUES (?, ?, ?)",
            (isim, telefon, mesaj)
        )
        return cursor.lastrowid


def tum_leadler():
    # En yeni kayıtları önce getir
    with get_db() as db:
        kayitlar = db.execute(
            "SELECT * FROM leads ORDER BY tarih DESC, id DESC"
        ).fetchall()

        return [dict(kayit) for kayit in kayitlar]