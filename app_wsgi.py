import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir, mode=0o755)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
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

# Add application directory to Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_APP'] = 'app.py'

try:
    # Import the Flask application
    from app import app as application
    logger.info("Flask application imported successfully")
except Exception as e:
    logger.error(f"Error importing Flask application: {str(e)}")
    raise

# Error handlers
@application.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error occurred: {str(error)}")
    return "We're sorry, but something went wrong. The issue has been logged for investigation.", 500

@application.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error occurred: {str(error)}")
    return "The requested resource was not found.", 404 