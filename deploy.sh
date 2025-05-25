#!/bin/bash

# Configuration
REMOTE_USER="ddiemeo9zafc"
REMOTE_HOST="contactbook.oerna.de"
REMOTE_DIR="~/mapcontacts"

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
echo "Creating temporary directory: $TEMP_DIR"

# Copy files to temporary directory, excluding unnecessary files
echo "Preparing files for deployment..."
cp -r app.py wsgi.py passenger_wsgi.py requirements.txt setup.py .python-version install_packages.sh static $TEMP_DIR/
cp -r .htaccess $TEMP_DIR/

# Sync files to server
echo "Deploying files to server..."
scp -r $TEMP_DIR/* $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

# Clean up
echo "Cleaning up..."
rm -rf $TEMP_DIR

echo "Deployment completed!"
echo "Please run the installation script on the server using the DomainFactory control panel." 