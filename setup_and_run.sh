#!/bin/bash

# User should ensure Python3, python3-venv, and python3-pip are installed.
# This script assumes they are available in the user's PATH.

# Navigate to the project directory (assuming script is run from project root or a user-writable path)
# cd /path/to/your/nslookup_app 
# Or, if running from within the directory:
# cd "$(dirname "$0")" # If script is inside the project dir

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages
pip install --upgrade pip
pip install -r requirements.txt # Ensure Flask, gunicorn/waitress are in requirements.txt

# Create a WSGI entry point if it doesn't exist (if using gunicorn)
if [ ! -f "wsgi.py" ]; then
    cat <<EOL > wsgi.py
from app import app

if __name__ == "__main__":
    app.run() # Or use waitress here if preferred for consistency
EOL
fi

echo "Starting the Flask application..."
# Start with Gunicorn on a non-privileged port
gunicorn --bind 0.0.0.0:8080 wsgi:app --timeout 120 --log-level debug --access-logfile - --error-logfile -
# Or with Waitress:
# python -m waitress --host=0.0.0.0 --port=8080 app:app
