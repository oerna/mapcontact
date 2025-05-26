import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir, mode=0o755)

# Configure logging to both file and console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add file handler
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'passenger.log'),
    maxBytes=10485760,  # 10MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Add application directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), '..')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_APP'] = os.path.join(app_dir, 'app.py')
os.environ['PYTHONPATH'] = app_dir

# Log startup information
logger.info(f"Application directory: {app_dir}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Files in current directory: {os.listdir('.')}")
logger.info(f"Environment variables: FLASK_ENV={os.environ.get('FLASK_ENV')}, FLASK_APP={os.environ.get('FLASK_APP')}, PYTHONPATH={os.environ.get('PYTHONPATH')}")

try:
    # Import the Flask application
    from app import app as application
    logger.info("Flask application imported successfully")
except Exception as e:
    logger.error(f"Error importing Flask application: {str(e)}")
    logger.error(f"Python version: {sys.version}")
    logger.error(f"Python executable: {sys.executable}")
    logger.error(f"Current working directory: {os.getcwd()}")
    logger.error(f"Directory contents: {os.listdir('.')}")
    raise 