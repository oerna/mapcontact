import sys, os
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
log_dir = os.path.join(os.getcwd(), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'passenger.log')
handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)

# Log the current working directory and Python path
logging.debug(f"Current working directory: {os.getcwd()}")
logging.debug(f"Python path: {sys.path}")

# Add the application directory to Python path
app_dir = '/home/ddiemeo9zafc/mapcontacts'
sys.path.insert(0, app_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_APP'] = 'app.py'
os.environ['PYTHONPATH'] = '/home/ddiemeo9zafc/virtualenv/mapcontacts/3.9/lib/python3.9/site-packages'
os.environ['DATABASE_URL'] = 'postgresql://ddiemeo9zafc:your_password@localhost:5432/ddiemeo9zafc'
os.environ['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure key

try:
    # Import the Flask application
    from app import app
    application = app
    logging.info("Successfully imported Flask application")
except Exception as e:
    logging.error(f"Failed to import Flask application: {str(e)}")
    raise 