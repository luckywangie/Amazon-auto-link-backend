from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Vehicle, Category, User

vehicle_bp = Blueprint('vehicle_bp', __name__)

# ✅ Public: View all available vehicles with filtering
@vehicle_bp.route('/', methods=['GET'])
def get_vehicles():
    category_name = request.args.get('category')  # e.g., 'SUV'
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    available = request.args.get('available')  # 'true' or 'false'

    query = Vehicle.query

    # Filter by availability
    if available == 'true':
        query = query.filter_by(availability=True)
    elif available == 'false':
        query = query.filter_by(availability=False)

    # Filter by category name (case-insensitive)
    if category_name:
        query = query.join(Category).filter(Category.name.ilike(category_name))

    # Filter by price range
    if min_price is not None:
        query = query.filter(Vehicle.price >= min_price)
    if max_price is not None:
        query = query.filter(Vehicle.price <= max_price)

    vehicles = query.all()
    return jsonify([{
        'id': v.id,
        'name': v.name,
        'description': v.description,
        'price': v.price,
        'availability': v.availability,
        'category': v.category.name if v.category else None,
        'image_url': v.image_url if v.image_url else None  # Ensure image_url is returned
    } for v in vehicles]), 200


# ✅ Public: Get vehicle by ID
@vehicle_bp.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    return jsonify({
        'id': vehicle.id,
        'name': vehicle.name,
        'description': vehicle.description,
        'price': vehicle.price,
        'availability': vehicle.availability,
        'category': vehicle.category.name if vehicle.category else None,
        'image_url': vehicle.image_url if vehicle.image_url else None  # Ensure image_url is returned
    }), 200


# ✅ Admin: Add a new vehicle
@vehicle_bp.route('/', methods=['POST'])
@jwt_required()
def add_vehicle():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    data = request.get_json()
    required_fields = ['name', 'description', 'price', 'category_id']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Validate image_url if provided
    image_url = data.get('image_url')
    if image_url and not isinstance(image_url, str):
        return jsonify({'error': 'image_url must be a string'}), 400

    vehicle = Vehicle(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        availability=data.get('availability', True),
        category_id=data['category_id'],
        image_url=image_url  # Store the image URL
    )
    db.session.add(vehicle)
    db.session.commit()
    return jsonify({
        'message': 'Vehicle added successfully',
        'vehicle': {
            'id': vehicle.id,
            'name': vehicle.name,
            'image_url': vehicle.image_url
        }
    }), 201


# ✅ Admin: Update a vehicle
@vehicle_bp.route('/<int:vehicle_id>', methods=['PATCH'])
@jwt_required()
def update_vehicle(vehicle_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    data = request.get_json()
    
    # Validate image_url if provided
    if 'image_url' in data and not isinstance(data['image_url'], str):
        return jsonify({'error': 'image_url must be a string'}), 400

    vehicle.name = data.get('name', vehicle.name)
    vehicle.description = data.get('description', vehicle.description)
    vehicle.price = data.get('price', vehicle.price)
    vehicle.availability = data.get('availability', vehicle.availability)
    vehicle.category_id = data.get('category_id', vehicle.category_id)
    vehicle.image_url = data.get('image_url', vehicle.image_url)  # Update image URL

    db.session.commit()
    return jsonify({
        'message': 'Vehicle updated successfully',
        'vehicle': {
            'id': vehicle.id,
            'name': vehicle.name,
            'image_url': vehicle.image_url
        }
    }), 200


# ✅ Admin: Delete a vehicle
@vehicle_bp.route('/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': 'Vehicle deleted'}), 200