import os
import sys

# Set the current working directory
os.chdir('/home/ddiemeo9zafc/mapcontacts')

# Add the application directory to the Python path
sys.path.insert(0, '/home/ddiemeo9zafc/mapcontacts')

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_APP'] = 'app.py'
os.environ['PYTHONPATH'] = '/home/ddiemeo9zafc/mapcontacts'
os.environ['DATABASE_URL'] = 'mysql://oernamann:gM0%k-4Ezxzr@localhost/contactmap_postgre'
os.environ['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Import the Flask application
from app import app as application 