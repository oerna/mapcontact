#!/bin/bash

echo "Starting installation..."

# Show Python version and path
echo "Python version:"
python3 --version
echo "Python path:"
which python3

# Create and activate virtual environment
echo "Setting up virtual environment..."
python3 -m venv /home/ddiemeo9zafc/virtualenv/mapcontacts/3.6
source /home/ddiemeo9zafc/virtualenv/mapcontacts/3.6/bin/activate

# Install packages in virtual environment
echo "Installing packages in virtual environment..."
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs
chmod 755 logs

# Set proper permissions
echo "Setting permissions..."
chmod -R 755 /home/ddiemeo9zafc/mapcontacts
chmod -R 755 /home/ddiemeo9zafc/virtualenv/mapcontacts

# Create a test WSGI file
echo "Creating test WSGI file..."
cat > test.wsgi << 'EOF'
def application(environ, start_response):
    status = '200 OK'
    output = b'Hello World!'
    response_headers = [('Content-type', 'text/plain'),
                       ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]
EOF

echo "Done!" 