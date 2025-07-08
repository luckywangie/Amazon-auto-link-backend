from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
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
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1]
            decoded_token = verify_firebase_token(token)
            
            if not decoded_token:
                return jsonify({'error': 'Invalid token'}), 401
            
            # Get or create user based on Firebase UID
            firebase_uid = decoded_token['uid']
            user = User.query.filter_by(firebase_uid=firebase_uid).first()
            
            if not user:
                # Create user if doesn't exist
                user = User(
                    firebase_uid=firebase_uid,
                    name=decoded_token.get('name', ''),
                    email=decoded_token.get('email', ''),
                    is_admin=False
                )
                db.session.add(user)
                db.session.commit()
            
            # Add user to request context
            request.current_user = user
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@booking_bp.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

@booking_bp.route('/', methods=['POST', 'OPTIONS'])
@cross_origin()
@firebase_auth_required
def create_booking():
    try:
        user = request.current_user
        
        if not user:
            logger.error("User not found in request context")
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        logger.info(f"Received booking data: {data}")

        # Required fields
        required_fields = [
            'vehicle_id', 'start_date', 'end_date', 'full_name', 'phone',
            'email', 'id_number', 'driving_license', 'pickup_option',
            'payment_method', 'total_price'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Validate vehicle
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle or not vehicle.availability:
            logger.error(f"Vehicle not available: {data['vehicle_id']}")
            return jsonify({'error': 'Vehicle not available'}), 404

        # Validate dates
        try:
            start = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end = datetime.strptime(data['end_date'], '%Y-%m-%d')
            
            if start >= end:
                logger.error("End date must be after start date")
                return jsonify({'error': 'End date must be after start date'}), 400
                
            if start.date() < datetime.now().date():
                logger.error("Start date cannot be in the past")
                return jsonify({'error': 'Start date cannot be in the past'}), 400
                
        except ValueError as e:
            logger.error(f"Invalid date format: {str(e)}")
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Validate delivery address if needed
        if data['pickup_option'] == 'delivery' and not data.get('delivery_address'):
            logger.error("Delivery address required for delivery option")
            return jsonify({'error': 'Delivery address is required for delivery option'}), 400

        # Create booking
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
            booking_status='pending'  # Use booking_status instead of status
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
@cross_origin()
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
@cross_origin()
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
@cross_origin()
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
@cross_origin()
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