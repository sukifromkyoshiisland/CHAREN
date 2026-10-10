from flask import Flask
from app.database import init_db


def create_app():
    # Flask uygulamasını oluştur
    app = Flask(__name__)

    # Veritabanını hazırla
    init_db(app)

    # Sayfa rotalarını uygulamaya bağla
    from app.routes import main
    app.register_blueprint(main)

    return app