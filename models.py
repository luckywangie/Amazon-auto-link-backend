from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class TokenBlocklist(db.Model):
    """Legacy JWT token blocklist (can be removed after Firebase migration)"""
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(256), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True)  # New Firebase UID field
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Made nullable for Firebase users
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Optional for users who register via email/password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Optional for users who register via email/password"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def _repr_(self):
        return f"<User {self.email}>"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image_url = db.Column(db.String(255))  # Added for category images
    vehicles = db.relationship('Vehicle', backref='category', lazy=True, cascade="all, delete-orphan")

    def _repr_(self):
        return f"<Category {self.name}>"

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(255))  # Main image URL
    image_urls = db.Column(db.JSON)  # Array of additional image URLs as JSON
    features = db.Column(db.JSON)  # Array of features as JSON
    seats = db.Column(db.Integer)
    transmission = db.Column(db.String(50))  # automatic/manual
    fuel_type = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    bookings = db.relationship('Booking', backref='vehicle', lazy=True, cascade="all, delete-orphan")

    def _repr_(self):
        return f"<Vehicle {self.name}>"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)  # Added calculated field
    full_name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    id_number = db.Column(db.String(50), nullable=False)
    driving_license = db.Column(db.String(50), nullable=False)
    pickup_option = db.Column(db.String(20), nullable=False)  # 'pickup' or 'delivery'
    delivery_address = db.Column(db.String(255))
    need_driver = db.Column(db.Boolean, default=False)
    driver_fee = db.Column(db.Float, default=0.0)  # Added driver fee
    special_requests = db.Column(db.Text)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(50), default='pending')  # Renamed from 'status'
    booking_status = db.Column(db.String(50), default='confirmed')  # confirmed/cancelled/completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def calculate_total(self, vehicle_price):
        """Calculate total price including driver fee if needed"""
        days = (self.end_date - self.start_date).days + 1
        self.total_price = days * vehicle_price
        if self.need_driver:
            self.driver_fee = 1000 * days  # Example: 1000 per day for driver
            self.total_price += self.driver_fee
        return self.total_price

    def _repr_(self):
        return f"<Booking {self.id}>"