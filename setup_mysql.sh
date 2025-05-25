#!/bin/bash

# Configuration
REMOTE_USER="ddiemeo9zafc"
REMOTE_HOST="contactbook.oerna.de"
REMOTE_DIR="/home/ddiemeo9zafc/mapcontacts"
VENV_PATH="/home/ddiemeo9zafc/virtualenv/mapcontacts/3.9"
MYSQL_URL="mysql://oernamann:gM0%k-4Ezxzr@localhost/contactmap_postgre"

export DATABASE_URL="$MYSQL_URL"

echo "Starting deployment and setup..."

# Deploy changes
echo "Deploying changes..."
./deploy.sh

# Setup database and install requirements
echo "Setting up database and installing requirements..."
ssh $REMOTE_USER@$REMOTE_HOST << EOF
    cd $REMOTE_DIR
    export DATABASE_URL="$MYSQL_URL"
    $VENV_PATH/bin/pip install -r requirements.txt

    # Create database tables
    DATABASE_URL="$MYSQL_URL" $VENV_PATH/bin/python3 - <<PYTHON
from app import db, app
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
PYTHON

    # Run migration script
    DATABASE_URL="$MYSQL_URL" $VENV_PATH/bin/python3 migrate_db.py

    # Restart application
    touch passenger_wsgi.py
EOF

echo "Setup completed! The application should now be using MySQL."
echo "Please check the application at https://contactbook.oerna.de" 