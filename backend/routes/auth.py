from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _public_user(user):
    """Strip password_hash before ever sending a user back to the client."""
    return {k: v for k, v in user.items() if k != "password_hash"}


@auth_bp.post("/register")
def register():
    data = request.get_json(force=True) or {}
    username = data.get("username")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    address = data.get("address")
    caregiver_name = data.get("caregiver_name") or data.get("c-name")
    caregiver_phone = data.get("caregiver_phone") or data.get("c-phone")
    birthday = data.get("birthday")
    language = data.get("language")
    medicines = data.get("medicines")

    if not username or not name or not email or not password:
        return jsonify({"error": "username, name, email, and password are required"}), 400

    if db.get_user_by_username(username):
        return jsonify({"error": "this username is already taken"}), 409

    if db.get_user_by_email(email):
        return jsonify({"error": "an account with this email already exists"}), 409

    password_hash = generate_password_hash(password)
    user = db.create_user(
        username, name, email, password_hash,
        phone=phone, address=address,
        caregiver_name=caregiver_name, caregiver_phone=caregiver_phone,
        birthday=birthday, language=language, medicines=medicines,
    )
    return jsonify(_public_user(user)), 201

@auth_bp.post("/login")
def login():
    """Matches the new login.html's fields: username, password."""
    data = request.get_json(force=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = db.get_user_by_username(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "invalid username or password"}), 401

    return jsonify(_public_user(user)), 200