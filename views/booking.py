from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Booking, Vehicle, User
from datetime import datetime

booking_bp = Blueprint('booking_bp', __name__)

# ✅ User: Book a vehicle
@booking_bp.route('/', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    data = request.get_json()

    # Required fields
    vehicle_id = data.get('vehicle_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    full_name = data.get('full_name')
    phone = data.get('phone')
    email = data.get('email')
    id_number = data.get('id_number')
    driving_license = data.get('driving_license')
    pickup_option = data.get('pickup_option')
    payment_method = data.get('payment_method')

    # Optional fields
    delivery_address = data.get('delivery_address')
    need_driver = data.get('need_driver', False)
    special_requests = data.get('special_requests', '')

    # Validate required fields
    if not all([vehicle_id, start_date, end_date, full_name, phone, email, 
                id_number, driving_license, pickup_option, payment_method]):
        return jsonify({'error': 'All required fields must be provided'}), 400

    # Validate delivery address if delivery option is selected
    if pickup_option == 'delivery' and not delivery_address:
        return jsonify({'error': 'Delivery address is required for delivery option'}), 400

    # Check if vehicle exists and is available
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle or not vehicle.availability:
        return jsonify({'error': 'Vehicle not available'}), 404

    # Validate date format and logic
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if start >= end:
        return jsonify({'error': 'End date must be after start date'}), 400

    # Check if dates are not in the past
    if start.date() < datetime.now().date():
        return jsonify({'error': 'Start date cannot be in the past'}), 400

    # Create new booking with all the information
    new_booking = Booking(
        user_id=user.id,
        vehicle_id=vehicle_id,
        start_date=start.date(),
        end_date=end.date(),
        full_name=full_name,
        phone=phone,
        email=email,
        id_number=id_number,
        driving_license=driving_license,
        pickup_option=pickup_option,
        delivery_address=delivery_address,
        need_driver=need_driver,
        special_requests=special_requests,
        payment_method=payment_method,
        status='pending'
    )
    
    try:
        db.session.add(new_booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking request submitted successfully',
            'booking_id': new_booking.id,
            'status': 'pending'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create booking. Please try again.'}), 500


# ✅ User: View own bookings
@booking_bp.route('/my', methods=['GET'])
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