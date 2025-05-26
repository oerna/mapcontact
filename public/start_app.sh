#!/bin/bash

# Enable error handling
set -e
set -o pipefail

# Set up logging
exec 1> >(tee -a "/home/ddiemeo9zafc/mapcontacts/public/app.log")
exec 2> >(tee -a "/home/ddiemeo9zafc/mapcontacts/public/app.log" >&2)

echo "=== Starting Flask application ==="
echo "Current time: $(date)"
echo "Current user: $(whoami)"
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "PATH: $PATH"

# Set up environment
export PYTHONPATH="/home/ddiemeo9zafc/mapcontacts"
export FLASK_APP="/home/ddiemeo9zafc/mapcontacts/app.py"
export FLASK_ENV="production"
export PATH="/home/ddiemeo9zafc/.local/bin:$PATH"

# Verify Python environment
echo "Python executable: $(which python3)"
echo "Gunicorn executable: $(which gunicorn)"
echo "PYTHONPATH: $PYTHONPATH"
echo "FLASK_APP: $FLASK_APP"

# Change to application directory
cd /home/ddiemeo9zafc/mapcontacts

# List directory contents for debugging
echo "Directory contents:"
ls -la

# Start Gunicorn with detailed error logging
echo "Starting Gunicorn..."
exec gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile /home/ddiemeo9zafc/mapcontacts/public/app.log \
    --error-logfile /home/ddiemeo9zafc/mapcontacts/public/app.log \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance \
    app:app 