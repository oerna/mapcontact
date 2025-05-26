#!/bin/bash

# Exit on any error
set -e

# Log file setup
LOG_FILE="deploy.log"
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

echo "=== Starting deployment at $(date) ==="

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        log "✓ $1"
    else
        log "✗ $1"
        exit 1
    fi
}

# 1. Environment Setup
log "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
check_status "Virtual environment created"

# 2. Install Dependencies
log "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
check_status "Dependencies installed"

# 3. Create Required Directories
log "Creating required directories..."
mkdir -p logs instance
chmod 755 logs instance
check_status "Directories created"

# 4. Database Setup
log "Setting up database..."
python3 migrate_db.py
check_status "Database setup completed"

# 5. Test Application
log "Testing application..."
python3 -c "from app import app; print('Application loaded successfully')"
check_status "Application test passed"

# 6. Set Permissions
log "Setting permissions..."
chmod -R 755 .
check_status "Permissions set"

echo "=== Deployment completed successfully at $(date) ==="
echo "Please check $LOG_FILE for detailed logs" 