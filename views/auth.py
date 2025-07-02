from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt
)
from flask_cors import cross_origin
from models import db, User, TokenBlocklist
from datetime import datetime, timezone, timedelta

auth_bp = Blueprint("auth_bp", __name__)

# === REGISTER ===
@auth_bp.route("/register", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://127.0.0.1:5173"], supports_credentials=True)
def register():
    if request.method == "OPTIONS":
        return '', 200  # Allow preflight

    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    new_user = User(name=name, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201

# === LOGIN ===
@auth_bp.route("/login", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://127.0.0.1:5173"], supports_credentials=True)
def login():
    if request.method == "OPTIONS":
        return '', 200  # Allow preflight

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
        return jsonify({"message": "Login successful", "token": access_token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# === FETCH CURRENT USER ===
@auth_bp.route("/current_user", methods=["GET", "OPTIONS"])
@jwt_required()
@cross_origin(origins=["http://127.0.0.1:5173"], supports_credentials=True)
def current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin
    }), 200

# === LOGOUT ===
@auth_bp.route("/logout", methods=["DELETE", "OPTIONS"])
@jwt_required()
@cross_origin(origins=["http://127.0.0.1:5173"], supports_credentials=True)
def logout():
    if request.method == "OPTIONS":
        return '', 200

    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)

    new_block = TokenBlocklist(jti=jti, created_at=now)
    db.session.add(new_block)
    db.session.commit()

    return jsonify({"message": "Logged out successfully"}), 200
