#!/bin/bash

# Set up environment
export PYTHONPATH=/home/ddiemeo9zafc/mapcontacts
export FLASK_APP=app.py
export FLASK_ENV=production

# Change to application directory
cd /home/ddiemeo9zafc/mapcontacts

# Kill any existing process
if [ -f app.pid ]; then
    old_pid=$(cat app.pid)
    if [ -d /proc/$old_pid ]; then
        kill $old_pid
        sleep 1
    fi
    rm app.pid
fi

# Start Gunicorn
exec gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 1 \
    --timeout 120 \
    --access-logfile /home/ddiemeo9zafc/mapcontacts/public/app.log \
    --error-logfile /home/ddiemeo9zafc/mapcontacts/public/app.log \
    --capture-output \
    --log-level debug \
    app:app 