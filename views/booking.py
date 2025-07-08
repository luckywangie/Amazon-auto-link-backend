from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from models import db, Booking, Vehicle, User
from datetime import datetime
import logging

booking_bp = Blueprint('booking_bp', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
@jwt_required()
def create_booking():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            logger.error(f"User not found with ID: {user_id}")
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
            status='pending'
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
@jwt_required()
def get_my_bookings():
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            'id': b.id,
            'vehicle': b.vehicle.name,
            'start_date': b.start_date.isoformat(),
            'end_date': b.end_date.isoformat(),
            'status': b.status,
            'full_name': b.full_name,
            'phone': b.phone,
            'pickup_option': b.pickup_option,
            'need_driver': b.need_driver,
            'payment_method': b.payment_method
        } for b in bookings
    ]), 200


# ✅ User: Cancel a booking
@booking_bp.route('/<int:booking_id>/cancel', methods=['PATCH'])
@cross_origin()
@jwt_required()
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()

    if not booking:
        return jsonify({'error': 'Booking not found or unauthorized'}), 404

    if datetime.utcnow().date() >= booking.start_date:
        return jsonify({'error': 'Cannot cancel after start date'}), 400

    booking.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Booking cancelled'}), 200


# ✅ Admin: View all bookings
@booking_bp.route('/', methods=['GET'])
@cross_origin()
@jwt_required()
def get_all_bookings():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    user_filter = request.args.get('user_id')
    status_filter = request.args.get('status')

    query = Booking.query

    if user_filter:
        query = query.filter_by(user_id=user_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    bookings = query.all()
    return jsonify([
        {
            'id': b.id,
            'user': b.user.name,
            'vehicle': b.vehicle.name,
            'start_date': b.start_date.isoformat(),
            'end_date': b.end_date.isoformat(),
            'status': b.status,
            'full_name': b.full_name,
            'phone': b.phone,
            'email': b.email,
            'pickup_option': b.pickup_option,
            'need_driver': b.need_driver,
            'payment_method': b.payment_method
        } for b in bookings
    ]), 200


# ✅ Admin: Update booking status
@booking_bp.route('/<int:booking_id>/status', methods=['PATCH'])
@cross_origin()
@jwt_required()
def update_booking_status(booking_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Admins only'}), 403

    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['pending', 'confirmed', 'completed', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400

    booking = Booking.query.filter_by(id=booking_id).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    booking.status = new_status
    db.session.commit()
    return jsonify({'message': 'Booking status updated'}), 200