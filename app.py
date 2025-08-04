import os
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from models import db
from views.firebase_config import initialize_firebase

# Blueprint imports
from views.auth import auth_bp
from views.user import user_bp
from views.category import category_bp
from views.vehicle import vehicle_bp
from views.booking import booking_bp

# Initialize Firebase
initialize_firebase()

# App Initialization
app = Flask(__name__)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ach_db_user:8CpLfVmu1LGoU2oE1hbwPX9RHLb7dL9E@dpg-d28foqhr0fns73dcr6f0-a.oregon-postgres.render.com/ach_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)

# CORS Configuration (updated for development/testing)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(category_bp, url_prefix='/categories')
app.register_blueprint(vehicle_bp, url_prefix='/vehicles')
app.register_blueprint(booking_bp, url_prefix='/api/bookings')

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
