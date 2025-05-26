#!/bin/bash

# Configuration
REMOTE_USER="ddiemeo9zafc"
REMOTE_HOST="contactbook.oerna.de"
REMOTE_DIR="~/mapcontacts"

# Create a temporary script to run on the server
cat > check_server_remote.sh << 'EOL'
#!/bin/bash

echo "=== Python Environment ==="
python3 --version
which python3
echo "Python path:"
python3 -c "import sys; print('\n'.join(sys.path))"

echo -e "\n=== Virtual Environment ==="
ls -la /home/ddiemeo9zafc/virtualenv/mapcontacts/3.9/bin/python3

echo -e "\n=== Application Logs ==="
if [ -f /home/ddiemeo9zafc/mapcontacts/logs/app.log ]; then
    tail -n 50 /home/ddiemeo9zafc/mapcontacts/logs/app.log
else
    echo "Application log file not found"
fi

echo -e "\n=== WSGI Bootstrap Log ==="
if [ -f /home/ddiemeo9zafc/mapcontacts/logs/wsgi_bootstrap.log ]; then
    tail -n 50 /home/ddiemeo9zafc/mapcontacts/logs/wsgi_bootstrap.log
else
    echo "WSGI bootstrap log file not found"
fi

echo -e "\n=== Apache Error Log ==="
if [ -f /var/log/apache2/error.log ]; then
    tail -n 50 /var/log/apache2/error.log
else
    echo "Apache error log not found"
    echo "Trying alternative locations..."
    for log in /var/log/httpd/error_log /var/log/apache2/error_log /var/log/httpd/error.log; do
        if [ -f "$log" ]; then
            echo "Found log at $log:"
            tail -n 50 "$log"
            break
        fi
    done
fi

echo -e "\n=== Directory Permissions ==="
ls -la /home/ddiemeo9zafc/mapcontacts
ls -la /home/ddiemeo9zafc/virtualenv/mapcontacts/3.9

echo -e "\n=== MySQL Connection Test ==="
python3 -c "
try:
    import MySQLdb
    conn = MySQLdb.connect(host='localhost', user='oernamann', passwd='gM0%k-4Ezxzr', db='contactmap_mysql')
    print('MySQL connection successful')
    conn.close()
except Exception as e:
    print('MySQL connection failed:', str(e))
"

echo -e "\n=== Installed Packages ==="
/home/ddiemeo9zafc/virtualenv/mapcontacts/3.9/bin/pip list
EOL

# Make the script executable
chmod +x check_server_remote.sh

# Copy and run the script on the server
echo "Running server checks..."
scp check_server_remote.sh $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_DIR && ./check_server_remote.sh"

# Clean up
rm check_server_remote.sh 