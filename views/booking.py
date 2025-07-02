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

    vehicle_id = data.get('vehicle_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not vehicle_id or not start_date or not end_date:
        return jsonify({'error': 'All fields are required'}), 400

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle or not vehicle.availability:
        return jsonify({'error': 'Vehicle not available'}), 404

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if start >= end:
        return jsonify({'error': 'End date must be after start date'}), 400

    new_booking = Booking(
        user_id=user.id,
        vehicle_id=vehicle_id,
        start_date=start,
        end_date=end,
        status='pending'
    )
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({'message': 'Booking request submitted'}), 201


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
            'status': b.status
        } for b in bookings
    ]), 200


# ✅ User: Cancel a booking
@booking_bp.route('/<int:booking_id>/cancel', methods=['PATCH'])
@jwt_required()
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.get(booking_id)

    if not booking or booking.user_id != user_id:
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
            'status': b.status
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

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    booking.status = new_status
    db.session.commit()
    return jsonify({'message': 'Booking status updated'}), 200
