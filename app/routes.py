
import os
import re
import hmac

from flask import Blueprint, render_template, request, jsonify, session

from app.database import (
    contact_ekle,
    tum_contactlar,
    subscriber_ekle,
    tum_subscriberlar,
    dashboard_istatistikleri
)

from app.services.ai_service import ai_service, AIServiceError


main = Blueprint("main", __name__)


# ANA SAYFA
@main.route("/")
def home():
    return render_template("index.html")


# WIX CHATBOT ARAYUZU
@main.route("/chat-widget")
def chat_widget():
    return render_template("chat_widget.html")


# ESKI HTML DASHBOARD
# Kisisel verilerin herkese acik olmamasi icin kapatildi.
@main.route("/dashboard")
def dashboard():
    return jsonify({"error": "Not Found"}), 404


# CONTACT FORM
@main.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name") or "").strip()
    email = str(data.get("email") or "").strip()
    message = str(data.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify({"error": "Missing required fields"}), 400

    if (
        len(name) > 150
        or len(email) > 254
        or len(message) > 5000
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    ):
        return jsonify({"error": "Invalid form data"}), 400

    contact_ekle(name, email, message)

    return jsonify({
        "success": True,
        "message": "Contact saved"
    }), 201


# NEWSLETTER
@main.route("/api/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email") or "").strip().lower()
    consent = data.get("consent")

    # Kullanici abonelik izni vermis olmali.
    if consent is not True:
        return jsonify({"error": "Consent is required"}), 400

    if (
        not email
        or len(email) > 254
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    ):
        return jsonify({"error": "Invalid email"}), 400

    created = subscriber_ekle(email)

    return jsonify({
        "success": True,
        "created": created
    }), 200


# ADMIN API AUTHENTICATION
def admin_authorized():
    expected_key = os.environ.get("ADMIN_API_KEY", "")
    supplied_key = request.headers.get("X-Admin-Key", "")

    return bool(
        expected_key
        and supplied_key
        and hmac.compare_digest(expected_key, supplied_key)
    )


# DASHBOARD OVERVIEW
@main.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    if not admin_authorized():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(dashboard_istatistikleri())


# DASHBOARD MESSAGES
@main.route("/api/admin/messages", methods=["GET"])
def admin_messages():
    if not admin_authorized():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(tum_contactlar())


# DASHBOARD SUBSCRIBERS
@main.route("/api/admin/subscribers", methods=["GET"])
def admin_subscribers():
    if not admin_authorized():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(tum_subscriberlar())


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

    gecmis = session.get("sohbet_gecmisi", [])

    try:
        yanit = ai_service.yanit_uret(
            mesaj,
            gecmis=gecmis
        )

        gecmis.append({
            "role": "user",
            "content": mesaj
        })

        gecmis.append({
            "role": "assistant",
            "content": yanit
        })

        session["sohbet_gecmisi"] = gecmis[-10:]

        return jsonify({
            "yanit": yanit
        })

    except AIServiceError:
        return jsonify({
            "error": "Çay asistanına şu anda ulaşılamıyor."
        }), 503
