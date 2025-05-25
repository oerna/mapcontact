import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the current working directory
os.chdir('/home/ddiemeo9zafc/mapcontacts')

# Add the application directory to the Python path
sys.path.insert(0, '/home/ddiemeo9zafc/mapcontacts')

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_APP'] = 'app.py'
os.environ['PYTHONPATH'] = '/home/ddiemeo9zafc/mapcontacts'
os.environ['DATABASE_URL'] = 'mysql://oernamann:gM0%k-4Ezxzr@localhost/contactmap_postgre'
os.environ['SECRET_KEY'] = 'mapcontacts-secure-key-2024'
os.environ['SESSION_COOKIE_SECURE'] = 'True'
os.environ['SESSION_COOKIE_HTTPONLY'] = 'True'
os.environ['SESSION_COOKIE_SAMESITE'] = 'Lax'
os.environ['PERMANENT_SESSION_LIFETIME'] = '86400'  # 24 hours in seconds
os.environ['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

# Log environment setup
logger.info("Environment configured for production")
logger.info(f"Database URL: {os.environ['DATABASE_URL']}")

# Import the Flask application
from app import app as application 