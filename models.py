from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(256), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    vehicles = db.relationship('Vehicle', backref='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(255))  # ✅ Added image_url field
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    bookings = db.relationship('Booking', backref='vehicle', lazy=True)

    def __repr__(self):
        return f"<Vehicle {self.name}>"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    id_number = db.Column(db.String(50), nullable=False)
    driving_license = db.Column(db.String(50), nullable=False)  # ✅ Already added
    pickup_option = db.Column(db.String(20), nullable=False)  # 'pickup' or 'delivery'
    delivery_address = db.Column(db.String(255))
    need_driver = db.Column(db.Boolean, default=False)
    special_requests = db.Column(db.Text)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):  # ✅ Fixed typo from _repr_ to __repr__
        return f"<Booking {self.id}>"
