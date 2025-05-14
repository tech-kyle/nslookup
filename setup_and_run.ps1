PowerShell
# User should ensure Python is installed and available in their PATH.
# This script assumes Python (with pip and venv) is user-accessible.

# Navigate to the project directory (assuming script is run from project root or a user-writable path)
# Set-Location -Path "C:\nslookup\nslookup_app"
# Or, if running from within the directory:
# Set-Location -Path $PSScriptRoot # If script is inside the project dir

# Create a virtual environment if it doesn't exist
if (-Not (Test-Path -Path "venv")) {
    python -m venv venv
}

# Activate the virtual environment
& .\venv\Scripts\Activate.ps1

# Install required Python packages
pip install --upgrade pip
pip install -r requirements.txt # Ensure Flask, waitress are in requirements.txt

# Start the Flask application using Waitress on a non-privileged port
Write-Output "Starting the Flask application using Waitress on port 8080..."
& .\venv\Scripts\python.exe -m waitress --host=0.0.0.0 --port=8080 app:app
