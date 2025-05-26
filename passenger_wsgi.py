import sys
import os
import logging

# Set up logging
logging.basicConfig(filename='/home/ddiemeo9zafc/mapcontacts/error.log',
                   level=logging.DEBUG,
                   format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

try:
    # Add your application directory to the Python path
    INTERP = os.path.expanduser("/home/ddiemeo9zafc/mapcontacts/venv/bin/python")
    if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)

    # Set the working directory
    os.chdir('/home/ddiemeo9zafc/mapcontacts')

    # Set environment variables
    os.environ['DATABASE_URL'] = 'mysql://ddiemeo9zafc_contacts:your_password@localhost/ddiemeo9zafc_contacts'
    os.environ['SECRET_KEY'] = 'your-secret-key-here'

    # Import your Flask app
    from app import app as application
    logger.info("Application loaded successfully")
except Exception as e:
    logger.error(f"Error loading application: {str(e)}")
    raise 