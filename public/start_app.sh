#!/bin/bash

# Enable error handling
set -e
set -o pipefail

# Set up logging
LOG_FILE="/home/ddiemeo9zafc/mapcontacts/public/app.log"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log "=== Starting Flask application ==="
log "Current time: $(date)"
log "Current user: $(whoami)"
log "Current directory: $(pwd)"

# Activate virtual environment
source /home/ddiemeo9zafc/virtualenv/mapcontacts/3.6/bin/activate

# Set up environment
export PYTHONPATH="/home/ddiemeo9zafc/mapcontacts"
export FLASK_APP="/home/ddiemeo9zafc/mapcontacts/app.py"
export FLASK_ENV="production"
export PYTHONUNBUFFERED=1

# Verify Python environment
log "Python executable: $(which python3)"
log "Python version: $(python3 --version)"
log "PYTHONPATH: $PYTHONPATH"
log "FLASK_APP: $FLASK_APP"

# Change to application directory
cd /home/ddiemeo9zafc/mapcontacts

# List directory contents for debugging
log "Directory contents:"
ls -la >> "$LOG_FILE" 2>&1

# Verify Gunicorn installation
if ! command -v gunicorn &> /dev/null; then
    log "ERROR: Gunicorn not found in virtual environment"
    exit 1
fi

# Verify Python packages
log "Checking Python packages..."
python3 -c "import flask; import flask_sqlalchemy; import flask_login; import flask_cors; import geopy; import gunicorn" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: Required Python packages not found"
    exit 1
fi

# Start Gunicorn with detailed error logging
log "Starting Gunicorn..."
exec gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile "$LOG_FILE" \
    --error-logfile "$LOG_FILE" \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance \
    --preload \
    app:app 