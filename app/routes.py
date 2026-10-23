import os
import re
import hmac

from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session
)

from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired
)

from app.database import (
    contact_ekle,
    tum_contactlar,
    subscriber_ekle,
    tum_subscriberlar,
    dashboard_istatistikleri,
    admin_dogrula
)

from app.services.ai_service import ai_service, AIServiceError


main = Blueprint("main", __name__)


# =====================================
# PUBLIC PAGES
# =====================================

@main.route("/")
def home():
    return render_template("index.html")


@main.route("/chat-widget")
def chat_widget():
    return render_template("chat_widget.html")


@main.route("/dashboard")
def dashboard():
    return jsonify({"error": "Not Found"}), 404


# =====================================
# CONTACT FORM
# =====================================

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


# =====================================
# NEWSLETTER
# =====================================

@main.route("/api/subscribe", methods=["POST"])
def subscribe():

    data = request.get_json(silent=True) or {}

    email = str(data.get("email") or "").strip().lower()
    consent = data.get("consent")

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


# =====================================
# ADMIN AUTHENTICATION
# =====================================

TOKEN_MAX_AGE = 60 * 60 * 2


def get_token_serializer():

    secret = os.environ.get("ADMIN_TOKEN_SECRET")

    if not secret:
        raise RuntimeError("ADMIN_TOKEN_SECRET is not configured")

    return URLSafeTimedSerializer(
        secret_key=secret,
        salt="charen-admin-auth-v1"
    )


def create_admin_token(admin):

    serializer = get_token_serializer()

    return serializer.dumps({
        "admin_id": admin["id"],
        "email": admin["email"]
    })


def verify_admin_token(token):

    if not token:
        return None

    try:
        serializer = get_token_serializer()

        return serializer.loads(
            token,
            max_age=TOKEN_MAX_AGE
        )

    except (BadSignature, SignatureExpired):
        return None


def admin_token_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        authorization = request.headers.get(
            "Authorization", ""
        )

        if not authorization.startswith("Bearer "):
            return jsonify({
                "error": "Authentication required"
            }), 401

        token = authorization[7:].strip()

        admin = verify_admin_token(token)

        if not admin:
            return jsonify({
                "error": "Invalid or expired session"
            }), 401

        return function(*args, **kwargs)

    return wrapper


# =====================================
# ADMIN LOGIN
# =====================================

@main.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json(silent=True) or {}

    email = str(data.get("email") or "").strip().lower()
    password = data.get("password")

    if (
        not email
        or not isinstance(password, str)
        or not password
    ):
        return jsonify({
            "error": "Email and password are required"
        }), 400

    admin = admin_dogrula(email, password)

    if not admin:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    token = create_admin_token(admin)

    return jsonify({
        "success": True,
        "token": token,
        "expires_in": TOKEN_MAX_AGE,
        "admin": {
            "email": admin["email"]
        }
    })


# =====================================
# ADMIN SESSION CHECK
# =====================================

@main.route("/api/admin/me", methods=["GET"])
@admin_token_required
def admin_me():

    return jsonify({
        "authenticated": True
    })


# =====================================
# DASHBOARD API
# =====================================

@main.route("/api/admin/stats", methods=["GET"])
@admin_token_required
def admin_stats():

    return jsonify(dashboard_istatistikleri())


@main.route("/api/admin/messages", methods=["GET"])
@admin_token_required
def admin_messages():

    return jsonify(tum_contactlar())


@main.route("/api/admin/subscribers", methods=["GET"])
@admin_token_required
def admin_subscribers():

    return jsonify(tum_subscriberlar())


# =====================================
# AI TEA SOMMELIER
# =====================================

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