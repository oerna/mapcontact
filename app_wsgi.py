import os
import sys
import logging
import traceback
from logging.handlers import RotatingFileHandler

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir, mode=0o755)

# Also log to a file in the public directory for easier access
public_log = os.path.join(os.path.dirname(__file__), 'public', 'error.log')
with open(public_log, 'w') as f:
    f.write("Starting application...\n")

logging.basicConfig(
    level=logging.DEBUG,
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

def log_error(message):
    with open(public_log, 'a') as f:
        f.write(f"{message}\n")

# Add application directory to Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

log_error(f"Application directory: {app_dir}")
log_error(f"Python path: {sys.path}")
log_error(f"Current working directory: {os.getcwd()}")
log_error(f"Files in current directory: {os.listdir('.')}")

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_APP'] = os.path.join(app_dir, 'app.py')
log_error(f"FLASK_APP set to: {os.environ['FLASK_APP']}")

try:
    # Import the Flask application
    from app import app as application
    log_error("Flask application imported successfully")
    log_error(f"Application path: {app_dir}")
    log_error(f"Python path: {sys.path}")
except Exception as e:
    error_msg = f"Error importing Flask application: {str(e)}\n{traceback.format_exc()}"
    log_error(error_msg)
    logger.error(error_msg)
    raise

# Error handlers
@application.errorhandler(500)
def internal_error(error):
    error_msg = f"500 error occurred: {str(error)}\n{traceback.format_exc()}"
    log_error(error_msg)
    logger.error(error_msg)
    return "We're sorry, but something went wrong. The issue has been logged for investigation.", 500

@application.errorhandler(404)
def not_found_error(error):
    error_msg = f"404 error occurred: {str(error)}"
    log_error(error_msg)
    logger.error(error_msg)
    return "The requested resource was not found.", 404 