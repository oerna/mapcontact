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
log "Python version: $(python3 --version)"
log "PATH: $PATH"

# Set up environment
export PYTHONPATH="/home/ddiemeo9zafc/mapcontacts"
export FLASK_APP="/home/ddiemeo9zafc/mapcontacts/app.py"
export FLASK_ENV="production"
export PATH="/home/ddiemeo9zafc/.local/bin:$PATH"
export PYTHONUNBUFFERED=1

# Verify Python environment
log "Python executable: $(which python3)"
log "PYTHONPATH: $PYTHONPATH"
log "FLASK_APP: $FLASK_APP"

# Change to application directory
cd /home/ddiemeo9zafc/mapcontacts

# List directory contents for debugging
log "Directory contents:"
ls -la >> "$LOG_FILE" 2>&1

# Start Gunicorn with detailed error logging
log "Starting Gunicorn..."
exec /home/ddiemeo9zafc/.local/bin/gunicorn \
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