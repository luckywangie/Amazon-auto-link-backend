from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models import db, User
from views.firebase_config import verify_firebase_token  


auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/verify_token", methods=["POST", "OPTIONS"])
@cross_origin(supports_credentials=True)
def verify_token():
    if request.method == "OPTIONS":
        return '', 200
    
    id_token = request.json.get('token')
    if not id_token:
        return jsonify({"error": "Token is required"}), 400
    
    decoded_token = verify_firebase_token(id_token)
    if not decoded_token:
        return jsonify({"error": "Invalid token"}), 401
    
    # Check if user exists in your database
    firebase_uid = decoded_token.get('uid')
    user = User.query.filter_by(firebase_uid=firebase_uid).first()
    
    if not user:
        # Create new user if doesn't exist
        email = decoded_token.get('email')
        name = decoded_token.get('name', email.split('@')[0])
        
        new_user = User(
            firebase_uid=firebase_uid,
            name=name,
            email=email
        )
        db.session.add(new_user)
        db.session.commit()
        user = new_user
    
    return jsonify({
        "message": "Authentication successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }), 200

@auth_bp.route("/current_user", methods=["GET", "OPTIONS"])
@cross_origin(supports_credentials=True)
def current_user():
    if request.method == "OPTIONS":
        return '', 200
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing"}), 401
    
    id_token = auth_header.split(' ')[1]
    decoded_token = verify_firebase_token(id_token)
    if not decoded_token:
        return jsonify({"error": "Invalid token"}), 401
    
    firebase_uid = decoded_token.get('uid')
    user = User.query.filter_by(firebase_uid=firebase_uid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin
    }), 200