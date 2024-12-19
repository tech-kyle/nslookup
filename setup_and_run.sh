#!/bin/bash

# Update and install necessary packages
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# Navigate to the project directory
cd /opt/python/nslookup

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages
pip install flask gunicorn

# Create a WSGI entry point
cat <<EOL > wsgi.py
from app import app

if __name__ == "__main__":
    app.run()
EOL

# Start the Flask application using gunicorn
gunicorn --bind 0.0.0.0:80 wsgi:app