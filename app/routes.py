from flask import Blueprint, render_template, request, jsonify

from app.database import tum_leadler
from app.services.ai_service import ai_service, AIServiceError


main = Blueprint("main", __name__)


# ANA SAYFA
@main.route("/")
def home():
    return render_template("index.html")


# YÖNETİM PANELİ
@main.route("/dashboard")
def dashboard():
    leadler = tum_leadler()

    return render_template(
        "dashboard.html",
        leadler=leadler
    )


# AI TEA SOMMELIER
@main.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    mesaj = data.get("mesaj", "")

    if not isinstance(mesaj, str) or not mesaj.strip():
        return jsonify({
            "error": "Lütfen bir mesaj yazın."
        }), 400

    mesaj = mesaj.strip()

    if len(mesaj) > 2000:
        return jsonify({
            "error": "Mesaj çok uzun."
        }), 400

    try:
        yanit = ai_service.yanit_uret(mesaj)

        return jsonify({
            "yanit": yanit
        })

    except AIServiceError:
        return jsonify({
            "error": "Çay asistanına şu anda ulaşılamıyor."
        }), 503