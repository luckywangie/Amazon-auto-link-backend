from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Category, User

category_bp = Blueprint('category_bp', __name__)

# ✅ Public: View all categories
@category_bp.route('/', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': cat.id,
        'name': cat.name
    } for cat in categories]), 200


# ✅ Admin: Create a new category
@category_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({'error': 'Category already exists'}), 409

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'Category added successfully'}), 201


# ✅ Admin: Update a category
@category_bp.route('/<int:category_id>', methods=['PATCH'])
@jwt_required()
def update_category(category_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    data = request.get_json()
    category.name = data.get('name', category.name)

    db.session.commit()
    return jsonify({'message': 'Category updated successfully'}), 200


# ✅ Admin: Delete a category
@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    if category.vehicles:  # assuming relationship exists
        return jsonify({'error': 'Cannot delete category with assigned vehicles'}), 400

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'}), 200