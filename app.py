import os
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from models import db

# Blueprint imports
from views.auth import auth_bp
from views.user import user_bp
from views.category import category_bp
from views.vehicle import vehicle_bp
from views.booking import booking_bp

# App Initialization
app = Flask(__name__)

# Absolute path to instance/app.db
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://alc_db_user:AubymIH05tNXldoGMXW7I0EVDD8TJR8i@dpg-d1iqen6mcj7s73enc3kg-a.oregon-postgres.render.com/alc_db"

# Other Configurations
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'       # replace with actual email
app.config['MAIL_PASSWORD'] = 'your_app_password'          # replace with actual app password

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
mail = Mail(app)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(category_bp, url_prefix='/categories')
app.register_blueprint(vehicle_bp, url_prefix='/vehicles')
app.register_blueprint(booking_bp, url_prefix='/bookings')

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
