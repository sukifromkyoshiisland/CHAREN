
import os

from flask import Flask
from app.database import init_db


def create_app():
    # Flask uygulamasını oluştur
    app = Flask(__name__)

    # Render'daki SECRET_KEY değerini Flask'a aktar
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    # Veritabanını hazırla
    init_db(app)

    # Sayfa rotalarını uygulamaya bağla
    from app.routes import main
    app.register_blueprint(main)

    return app
