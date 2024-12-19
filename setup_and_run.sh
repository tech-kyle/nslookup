#!/bin/bash

# Update and install necessary packages
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# Navigate to the project directory
cd /opt/python/nslookup

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages
pip install --upgrade pip
pip install flask gunicorn

# Create a WSGI entry point if it doesn't exist
if [ ! -f "wsgi.py" ]; then
    cat <<EOL > wsgi.py
from app import app

if __name__ == "__main__":
    app.run()
EOL
fi

# Start the Flask application using gunicorn with increased timeout
gunicorn --bind 0.0.0.0:80 wsgi:app --timeout 120 --log-level debug --access-logfile - --error-logfile -