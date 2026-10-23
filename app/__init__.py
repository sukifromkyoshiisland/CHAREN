import os
import sqlite3

from flask import Flask
from app.database import init_db, admin_ekle, get_db


def create_app():

    app = Flask(__name__)

    # Flask secret key
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    # Initialize database
    init_db(app)

    # =====================================
    # CREATE INITIAL ADMIN ACCOUNT
    # =====================================

    with app.app_context():

        admin_email = os.environ.get(
            "ADMIN_EMAIL", ""
        ).strip().lower()

        admin_password = os.environ.get(
            "ADMIN_PASSWORD", ""
        )

        if admin_email and admin_password:

            with get_db() as db:
                existing_admin = db.execute(
                    "SELECT id FROM admins WHERE email = ?",
                    (admin_email,)
                ).fetchone()

            if not existing_admin:

                try:
                    admin_ekle(
                        admin_email,
                        admin_password
                    )

                    app.logger.info(
                        "Initial admin account created"
                    )

                except sqlite3.IntegrityError:
                    app.logger.info(
                        "Admin account already exists"
                    )

        else:
            app.logger.warning(
                "Admin credentials not configured"
            )

    # Register routes
    from app.routes import main
    app.register_blueprint(main)

    return app