from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import csv
import io
import logging
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure instance directory exists with proper permissions
instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))
if not os.path.exists(instance_path):
    os.makedirs(instance_path, mode=0o755)

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mapcontacts-secure-key-2024')
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', '86400')))
app.config['SESSION_COOKIE_DOMAIN'] = 'contactbook.oerna.de' if os.environ.get('FLASK_ENV') == 'production' else None

# Configure CORS
CORS(app, 
     supports_credentials=True,
     resources={
         r"/*": {
             "origins": ["https://contactbook.oerna.de"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }
     })

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

# Database configuration
try:
    if os.environ.get('DATABASE_URL'):
        # Production database (MySQL)
        database_url = os.environ.get('DATABASE_URL')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        logger.info(f"Using production database: {database_url}")
    else:
        # Development database (SQLite)
        db_path = os.path.join(instance_path, 'contacts.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        logger.info(f"Using development database: {db_path}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    logger.info("Database connection configured successfully")
except Exception as e:
    logger.error(f"Database configuration error: {str(e)}")
    raise

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
    notes = db.Column(db.Text)
    contact_type = db.Column(db.String(50), nullable=True)
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
            'notes': self.notes,
            'contact_type': self.contact_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the database tables and admin user
with app.app_context():
    try:
        db.create_all()
        # Create default admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logger.info("Created admin user")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

@app.route('/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            logger.warning("Login attempt with non-JSON data")
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            logger.warning("Login attempt with missing credentials")
            return jsonify({'error': 'Missing username or password'}), 400
            
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            logger.warning(f"Login attempt with non-existent username: {data['username']}")
            return jsonify({'error': 'Invalid username or password'}), 401
            
        if not user.check_password(data['password']):
            logger.warning(f"Login attempt with incorrect password for user: {data['username']}")
            return jsonify({'error': 'Invalid username or password'}), 401
            
        login_user(user, remember=True)
        session.permanent = True
        logger.info(f"Successful login for user: {data['username']}")
        return jsonify({'message': 'Logged in successfully'})
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        session.clear()
        return redirect('/login.html')
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return redirect('/login.html')

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect('/login.html')
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
            notes=data.get('notes', ''),
            contact_type=data.get('contact_type', 'Other') or 'Other',
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
    try:
        if current_user.is_authenticated:
            return jsonify({'authenticated': True, 'user': current_user.username})
        return jsonify({'authenticated': False}), 401
    except Exception as e:
        logger.error(f"Auth check error: {str(e)}")
        return jsonify({'authenticated': False, 'error': str(e)}), 401

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
    print("=== DEBUG: Contact Update ===")
    print("Contact ID:", contact_id)
    print("Raw request data:", request.get_data())
    print("Parsed request data:", data)
    print("Current contact type:", contact.contact_type)
    print("Requested contact type:", data.get('contact_type'))
    
    # Update the contact fields
    contact.name = data.get('name', contact.name)
    contact.company = data.get('company', contact.company)
    contact.email = data.get('email', contact.email)
    contact.telephone = data.get('telephone', contact.telephone)
    contact.address = data.get('address', contact.address)
    contact.latitude = data.get('latitude', contact.latitude)
    contact.longitude = data.get('longitude', contact.longitude)
    contact.notes = data.get('notes', contact.notes)
    
    # Directly set contact_type from request data
    if 'contact_type' in data:
        print("Setting contact type to:", data['contact_type'])
        contact.contact_type = data['contact_type']
        db.session.flush()  # Flush changes to see if they're applied
        print("Contact type after flush:", contact.contact_type)
    
    print("Final contact type:", contact.contact_type)
    
    try:
        db.session.commit()
        print("Contact updated successfully")
        print("Returning contact data:", contact.to_dict())
        print("=== END DEBUG ===")
        return jsonify(contact.to_dict())
    except Exception as e:
        print("Error updating contact:", str(e))
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/export')
@login_required
def export_contacts():
    # Get all contacts for the current user
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    
    # Create a StringIO object to write CSV data
    si = io.StringIO()
    writer = csv.DictWriter(si, fieldnames=['name', 'company', 'email', 'telephone', 'address', 'latitude', 'longitude', 'notes', 'contact_type', 'user_id'])
    
    writer.writeheader()
    for contact in contacts:
        writer.writerow({
            'name': contact.name,
            'company': contact.company,
            'email': contact.email,
            'telephone': contact.telephone,
            'address': contact.address,
            'latitude': contact.latitude,
            'longitude': contact.longitude,
            'notes': contact.notes,
            'contact_type': contact.contact_type,
            'user_id': contact.user_id
        })
    
    output = si.getvalue()
    si.close()
    
    # Create a BytesIO object for the response
    bio = io.BytesIO()
    bio.write(output.encode('utf-8'))
    bio.seek(0)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'contacts_export_{timestamp}.csv'
    )

@app.route('/api/contacts/import', methods=['POST'])
@login_required
def import_contacts():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400

    imported_count = 0
    skipped_count = 0
    
    try:
        # Read the CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        
        for row in reader:
            # Check if contact already exists
            existing_contact = Contact.query.filter_by(
                name=row['name'],
                address=row['address'],
                user_id=current_user.id
            ).first()
            
            if existing_contact:
                skipped_count += 1
                continue
                
            try:
                # Create new contact
                new_contact = Contact(
                    name=row['name'],
                    company=row.get('company', ''),
                    email=row.get('email', ''),
                    telephone=row.get('telephone', ''),
                    address=row['address'],
                    latitude=float(row['latitude']) if row['latitude'] else None,
                    longitude=float(row['longitude']) if row['longitude'] else None,
                    notes=row.get('notes', ''),
                    contact_type=row.get('contact_type', 'Other') or 'Other',
                    user_id=current_user.id
                )
                
                # If coordinates are missing, geocode the address
                if not new_contact.latitude or not new_contact.longitude:
                    try:
                        location = geocoder.geocode(row['address'])
                        if location:
                            new_contact.latitude = location.latitude
                            new_contact.longitude = location.longitude
                        else:
                            continue
                    except GeocoderTimedOut:
                        continue
                
                db.session.add(new_contact)
                imported_count += 1
                
                # Commit every 10 records
                if imported_count % 10 == 0:
                    db.session.commit()
                    
            except Exception as e:
                continue
                
        # Final commit
        db.session.commit()
        
        return jsonify({
            'message': 'Import completed successfully',
            'imported': imported_count,
            'skipped': skipped_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'message': 'Contact deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True) 