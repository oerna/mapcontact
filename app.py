from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Ensure instance directory exists with proper permissions
instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))
if not os.path.exists(instance_path):
    os.makedirs(instance_path, mode=0o755)

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change this in production
CORS(app)

# Configure database with absolute path
db_path = os.path.join(instance_path, 'contacts.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize geocoder
geocoder = Nominatim(user_agent="mapcontacts")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    email = db.Column(db.String(120))
    telephone = db.Column(db.String(20))
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'email': self.email,
            'telephone': self.telephone,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the database tables
with app.app_context():
    db.create_all()
    # Create default admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('change-this-password')  # Change this password immediately after first login
        db.session.add(admin)
        db.session.commit()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'})
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/contacts', methods=['GET'])
@login_required
def get_contacts():
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    return jsonify([contact.to_dict() for contact in contacts])

@app.route('/api/contacts', methods=['POST'])
@login_required
def add_contact():
    data = request.json
    
    # Geocode the address
    try:
        location = geocoder.geocode(data['address'])
        if not location:
            return jsonify({'error': 'Could not geocode address'}), 400
            
        new_contact = Contact(
            name=data['name'],
            company=data.get('company', ''),
            email=data.get('email', ''),
            telephone=data.get('telephone', ''),
            address=data['address'],
            latitude=location.latitude,
            longitude=location.longitude,
            user_id=current_user.id
        )
        db.session.add(new_contact)
        db.session.commit()
        return jsonify(new_contact.to_dict()), 201
        
    except GeocoderTimedOut:
        return jsonify({'error': 'Geocoding service timed out'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-auth')
def check_auth():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False}), 401

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Both current and new passwords are required'}), 400
        
    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
        
    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'})

@app.route('/api/contacts/<int:contact_id>', methods=['PATCH'])
@login_required
def update_contact(contact_id):
    contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
        
    data = request.json
    
    # Update the contact fields
    contact.name = data.get('name', contact.name)
    contact.company = data.get('company', contact.company)
    contact.email = data.get('email', contact.email)
    contact.telephone = data.get('telephone', contact.telephone)
    contact.address = data.get('address', contact.address)
    contact.latitude = data.get('latitude', contact.latitude)
    contact.longitude = data.get('longitude', contact.longitude)
    
    try:
        db.session.commit()
        return jsonify(contact.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True) 