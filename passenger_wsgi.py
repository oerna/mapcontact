import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import traceback

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

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_APP'] = 'app.py'
os.environ['PYTHONPATH'] = '/home/ddiemeo9zafc/mapcontacts'
os.environ['DATABASE_URL'] = 'mysql://oernamann:gM0%25k-4Ezxzr@localhost/contactmap_postgre'
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

# Import the Flask application
from app import app as application
logger.info("Flask application imported successfully")

# Add error handlers
@application.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error occurred: {str(error)}")
    logger.error(f"Error details: {traceback.format_exc()}")
    return "We're sorry, but something went wrong. The issue has been logged for investigation. Please try again later.", 500

@application.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error occurred: {str(error)}")
    return "The requested resource was not found.", 404

@application.errorhandler(Exception)
def unhandled_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(f"Exception details: {traceback.format_exc()}")
    return "We're sorry, but something went wrong. The issue has been logged for investigation. Please try again later.", 500 