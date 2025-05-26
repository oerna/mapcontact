import sys
import os
import logging

# Set up logging
log_file = '/home/ddiemeo9zafc/mapcontacts/error.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)
with open(log_file, 'a') as f:
    pass  # Create file if it doesn't exist
os.chmod(log_file, 0o666)  # Make it writable

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Add your application directory to the Python path
    INTERP = os.path.expanduser("/home/ddiemeo9zafc/mapcontacts/venv/bin/python")
    if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)

    # Set the working directory
    os.chdir('/home/ddiemeo9zafc/mapcontacts')
    logger.info("Working directory set to: %s", os.getcwd())

    # Set environment variables
    os.environ['DATABASE_URL'] = 'mysql://ddiemeo9zafc_contacts:your_password@localhost/ddiemeo9zafc_contacts'
    os.environ['SECRET_KEY'] = 'your-secret-key-here'
    logger.info("Environment variables set")

    # Import your Flask app
    from app import app as application
    logger.info("Application loaded successfully")
except Exception as e:
    logger.error("Error loading application: %s", str(e), exc_info=True)
    raise 