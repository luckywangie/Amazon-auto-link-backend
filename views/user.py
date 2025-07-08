from flask import Blueprint, jsonify, request
from models import db, User
from views.firebase_config import verify_firebase_token  


user_bp = Blueprint('user_bp', __name__)

def get_current_user(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    id_token = auth_header.split(' ')[1]
    decoded_token = verify_firebase_token(id_token)
    if not decoded_token:
        return None
    
    firebase_uid = decoded_token.get('uid')
    return User.query.filter_by(firebase_uid=firebase_uid).first()

@user_bp.route('/me', methods=['GET'])
def get_my_profile():
    user = get_current_user(request)
    if not user:
        return jsonify({'error': 'User not found or unauthorized'}), 404
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'is_admin': user.is_admin
    }), 200

@user_bp.route('/me', methods=['PATCH'])
def update_my_profile():
    user = get_current_user(request)
    if not user:
        return jsonify({'error': 'User not found or unauthorized'}), 404
    
    data = request.get_json()
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

@user_bp.route('/', methods=['GET'])
def get_all_users():
    user = get_current_user(request)
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.all()
    return jsonify([
        {
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'is_admin': u.is_admin
        } for u in users
    ]), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    current_user = get_current_user(request)
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200