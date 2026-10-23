import sqlite3
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


# DATABASE CONNECTION
def get_db():
    connection = sqlite3.connect("charen.db")
    connection.row_factory = sqlite3.Row
    return connection


# INITIALIZE DATABASE
def init_db(app):
    with app.app_context():
        with get_db() as db:

            # Existing leads table
            db.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isim TEXT NOT NULL,
                    telefon TEXT NOT NULL,
                    mesaj TEXT,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Contact Form messages
            db.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Newsletter subscribers
            db.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # ADMIN USERS
            db.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


# EXISTING LEADS
def lead_ekle(isim, telefon, mesaj=""):
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO leads (isim, telefon, mesaj) VALUES (?, ?, ?)",
            (isim, telefon, mesaj)
        )
        return cursor.lastrowid


def tum_leadler():
    with get_db() as db:
        kayitlar = db.execute(
            "SELECT * FROM leads ORDER BY tarih DESC, id DESC"
        ).fetchall()

        return [dict(kayit) for kayit in kayitlar]


# CONTACT FORM
def contact_ekle(name, email, message):
    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO contacts (name, email, message)
            VALUES (?, ?, ?)
            """,
            (name, email, message)
        )
        return cursor.lastrowid


def tum_contactlar():
    with get_db() as db:
        kayitlar = db.execute(
            """
            SELECT * FROM contacts
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

        return [dict(kayit) for kayit in kayitlar]


# NEWSLETTER
def subscriber_ekle(email):
    with get_db() as db:
        cursor = db.execute(
            """
            INSERT OR IGNORE INTO subscribers (email)
            VALUES (?)
            """,
            (email,)
        )
        return cursor.rowcount > 0


def tum_subscriberlar():
    with get_db() as db:
        kayitlar = db.execute(
            """
            SELECT * FROM subscribers
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

        return [dict(kayit) for kayit in kayitlar]


# DASHBOARD STATISTICS
def dashboard_istatistikleri():
    with get_db() as db:
        total_messages = db.execute(
            "SELECT COUNT(*) FROM contacts"
        ).fetchone()[0]

        total_subscribers = db.execute(
            "SELECT COUNT(*) FROM subscribers"
        ).fetchone()[0]

    return {
        "totalMessages": total_messages,
        "totalSubscribers": total_subscribers
    }


# ADMIN AUTHENTICATION
def admin_ekle(email, password):
    password_hash = generate_password_hash(password)

    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO admins (email, password_hash)
            VALUES (?, ?)
            """,
            (email.strip().lower(), password_hash)
        )
        return cursor.lastrowid


def admin_dogrula(email, password):
    with get_db() as db:
        admin = db.execute(
            """
            SELECT id, email, password_hash
            FROM admins
            WHERE email = ?
            """,
            (email.strip().lower(),)
        ).fetchone()

    if admin and check_password_hash(admin["password_hash"], password):
        return {
            "id": admin["id"],
            "email": admin["email"]
        }

    return None