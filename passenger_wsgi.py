import sys
import os

# Add your application directory to the Python path
INTERP = os.path.expanduser("/home/ddiemeo9zafc/mapcontacts/venv/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Set the working directory
os.chdir('/home/ddiemeo9zafc/mapcontacts')

# Import your Flask app
from app import app as application 