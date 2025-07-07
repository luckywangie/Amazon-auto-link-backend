import os
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db

# Blueprint imports
from views.auth import auth_bp
from views.user import user_bp
from views.category import category_bp
from views.vehicle import vehicle_bp
from views.booking import booking_bp

# App Initialization
app = Flask(__name__)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://alc_db_user:AubymIH05tNXldoGMXW7I0EVDD8TJR8i@dpg-d1iqen6mcj7s73enc3kg-a.oregon-postgres.render.com/alc_db"

# Other Configurations
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'qwerty'

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# CORS Configuration - THIS IS THE KEY FIX
CORS(app, 
     origins=['http://localhost:5173', 'http://localhost:3000'],  # Add your frontend URLs
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(category_bp, url_prefix='/categories')
app.register_blueprint(vehicle_bp, url_prefix='/vehicles')
app.register_blueprint(booking_bp, url_prefix='/booking')  # Note: changed from /bookings to /booking to match your API call

# Run Server
if __name__ == '_main_':
    app.run(debug=True)