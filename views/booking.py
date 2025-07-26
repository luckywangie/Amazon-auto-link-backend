from flask import Blueprint, request, jsonify
from models import db, Booking, Vehicle, User
from views.firebase_config import verify_firebase_token
from datetime import datetime
import logging
from functools import wraps

booking_bp = Blueprint('booking_bp', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def firebase_auth_required(f):
    """Custom decorator for Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            decoded_token = verify_firebase_token(token)
            if not decoded_token:
                return jsonify({'error': 'Invalid token'}), 401

            firebase_uid = decoded_token['uid']
            user = User.query.filter_by(firebase_uid=firebase_uid).first()

            if not user:
                user = User(
                    firebase_uid=firebase_uid,
                    name=decoded_token.get('name', ''),
                    email=decoded_token.get('email', ''),
                    is_admin=False
                )
                db.session.add(user)
                db.session.commit()

            request.current_user = user

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401

        return f(*args, **kwargs)
    return decorated_function

@booking_bp.route('/', methods=['POST'])
@firebase_auth_required
def create_booking():
    try:
        user = request.current_user
        if not user:
            logger.error("User not found in request context")
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        logger.info(f"Received booking data: {data}")

        required_fields = [
            'vehicle_id', 'start_date', 'end_date', 'full_name', 'phone',
            'email', 'id_number', 'driving_license', 'pickup_option',
            'payment_method', 'total_price'
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle or not vehicle.availability:
            logger.error(f"Vehicle not available: {data['vehicle_id']}")
            return jsonify({'error': 'Vehicle not available'}), 404

        try:
            start = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end = datetime.strptime(data['end_date'], '%Y-%m-%d')
            if start >= end:
                return jsonify({'error': 'End date must be after start date'}), 400
            if start.date() < datetime.now().date():
                return jsonify({'error': 'Start date cannot be in the past'}), 400
        except ValueError as e:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        if data['pickup_option'] == 'delivery' and not data.get('delivery_address'):
            return jsonify({'error': 'Delivery address is required for delivery option'}), 400

        new_booking = Booking(
            user_id=user.id,
            vehicle_id=data['vehicle_id'],
            start_date=start.date(),
            end_date=end.date(),
            full_name=data['full_name'],
            phone=data['phone'],
            email=data['email'],
            id_number=data['id_number'],
            driving_license=data['driving_license'],
            pickup_option=data['pickup_option'],
            delivery_address=data.get('delivery_address'),
            need_driver=data.get('need_driver', False),
            special_requests=data.get('special_requests', ''),
            payment_method=data['payment_method'],
            total_price=data['total_price'],
            driver_fee=data.get('driver_fee', 0),
            booking_status='pending'
        )

        db.session.add(new_booking)
        db.session.commit()

        logger.info(f"Booking created successfully: {new_booking.id}")
        return jsonify({
            'message': 'Booking request submitted successfully',
            'booking_id': new_booking.id,
            'status': 'pending'
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating booking: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to create booking: {str(e)}'}), 500

@booking_bp.route('/my', methods=['GET'])
@firebase_auth_required
def get_my_bookings():
    user = request.current_user
    bookings = Booking.query.filter_by(user_id=user.id).all()
    return jsonify([
        {
            'id': b.id,
            'vehicle': b.vehicle.name,
            'start_date': b.start_date.isoformat(),
            'end_date': b.end_date.isoformat(),
            'status': b.booking_status,
            'full_name': b.full_name,
            'phone': b.phone,
            'pickup_option': b.pickup_option,
            'need_driver': b.need_driver,
            'payment_method': b.payment_method,
            'total_price': b.total_price
        } for b in bookings
    ]), 200

@booking_bp.route('/<int:booking_id>/cancel', methods=['PATCH'])
@firebase_auth_required
def cancel_booking(booking_id):
    user = request.current_user
    booking = Booking.query.filter_by(id=booking_id, user_id=user.id).first()

    if not booking:
        return jsonify({'error': 'Booking not found or unauthorized'}), 404

    if datetime.utcnow().date() >= booking.start_date:
        return jsonify({'error': 'Cannot cancel after start date'}), 400

    booking.booking_status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Booking cancelled'}), 200

@booking_bp.route('/', methods=['GET'])
@firebase_auth_required
def get_all_bookings():
    user = request.current_user
    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    user_filter = request.args.get('user_id')
    status_filter = request.args.get('status')

    query = Booking.query
    if user_filter:
        query = query.filter_by(user_id=user_filter)
    if status_filter:
        query = query.filter_by(booking_status=status_filter)

    bookings = query.all()
    return jsonify([
        {
            'id': b.id,
            'user': b.user.name,
            'vehicle': b.vehicle.name,
            'start_date': b.start_date.isoformat(),
            'end_date': b.end_date.isoformat(),
            'status': b.booking_status,
            'full_name': b.full_name,
            'phone': b.phone,
            'email': b.email,
            'pickup_option': b.pickup_option,
            'need_driver': b.need_driver,
            'payment_method': b.payment_method,
            'total_price': b.total_price
        } for b in bookings
    ]), 200

@booking_bp.route('/<int:booking_id>/status', methods=['PATCH'])
@firebase_auth_required
def update_booking_status(booking_id):
    user = request.current_user
    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['pending', 'confirmed', 'completed', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400

    booking = Booking.query.filter_by(id=booking_id).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    booking.booking_status = new_status
    db.session.commit()
    return jsonify({'message': 'Booking status updated'}), 200

@booking_bp.route('/<int:booking_id>', methods=['GET'])
@firebase_auth_required
def get_booking(booking_id):
    try:
        user = request.current_user
        if not user:
            return jsonify({'error': 'User not found'}), 404

        booking = Booking.query.get(booking_id) if user.is_admin else Booking.query.filter_by(id=booking_id, user_id=user.id).first()
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        booking_data = {
            'id': booking.id,
            'user_id': booking.user_id,
            'vehicle_id': booking.vehicle_id,
            'start_date': booking.start_date.isoformat(),
            'end_date': booking.end_date.isoformat(),
            'full_name': booking.full_name,
            'phone': booking.phone,
            'email': booking.email,
            'id_number': booking.id_number,
            'driving_license': booking.driving_license,
            'pickup_option': booking.pickup_option,
            'delivery_address': booking.delivery_address,
            'need_driver': booking.need_driver,
            'special_requests': booking.special_requests,
            'payment_method': booking.payment_method,
            'total_price': float(booking.total_price),
            'driver_fee': float(booking.driver_fee) if booking.driver_fee else 0,
            'booking_status': booking.booking_status,
            'created_at': booking.created_at.isoformat() if hasattr(booking, 'created_at') else None,
            'vehicle': {
                'id': booking.vehicle.id,
                'name': booking.vehicle.name,
                'description': booking.vehicle.description,
                'price': float(booking.vehicle.price),
                'image_url': booking.vehicle.image_url if hasattr(booking.vehicle, 'image_url') else None,
                'availability': booking.vehicle.availability
            }
        }

        return jsonify(booking_data), 200

    except Exception as e:
        logger.error(f"Error fetching booking {booking_id}: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to fetch booking: {str(e)}'}), 500
