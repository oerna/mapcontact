#!/usr/bin/env bash

# Create virtual environment in the correct location
/usr/bin/python3 -m venv /home/ddiemeo9zafc/virtualenv/mapcontacts

# Activate virtual environment
source /home/ddiemeo9zafc/virtualenv/mapcontacts/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
pip install -e .

# Create logs directory if it doesn't exist
mkdir -p /home/ddiemeo9zafc/mapcontacts/logs

# Set proper permissions
chmod -R 755 /home/ddiemeo9zafc/mapcontacts
chmod -R 755 /home/ddiemeo9zafc/virtualenv/mapcontacts

# Create a .htaccess file to point to the virtual environment
echo "AddHandler wsgi-script .wsgi
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,L]

# Set Python path
SetEnv PYTHONPATH /home/ddiemeo9zafc/mapcontacts/venv/lib/python3.9/site-packages" > .htaccess

# Make sure all files are readable
chmod -R 755 .
chmod -R 644 *.py *.txt
chmod 755 venv/bin/* 