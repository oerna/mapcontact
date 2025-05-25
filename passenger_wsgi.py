import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_dir = '/home/ddiemeo9zafc/mapcontacts/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir, mode=0o755)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
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
os.environ['SESSION_COOKIE_DOMAIN'] = 'contactbook.oerna.de'

# Log environment setup
logger.info("Environment configured for production")
logger.info(f"Database URL: {os.environ['DATABASE_URL']}")

try:
    # Import the Flask application
    from app import app as application
    logger.info("Flask application imported successfully")
except Exception as e:
    logger.error(f"Failed to import Flask application: {str(e)}")
    raise 