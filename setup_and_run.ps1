# Ensure script is run as Administrator
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Warning "You do not have Administrator rights to run this script!`nPlease re-run this script as an Administrator."
    exit
}

# Update and install necessary packages
Write-Output "Updating and installing necessary packages..."
choco install python -y

# Navigate to the project directory
Set-Location -Path "C:\nslookup"

# Create a virtual environment if it doesn't exist
if (-Not (Test-Path -Path "venv")) {
    python -m venv venv
}

# Activate the virtual environment
& .\venv\Scripts\Activate.ps1

# Install required Python packages
pip install --upgrade pip
pip install flask gunicorn

# Create a WSGI entry point if it doesn't exist
if (-Not (Test-Path -Path "wsgi.py")) {
    @"
from app import app

if __name__ == "__main__":
    app.run()
"@ | Out-File -FilePath "wsgi.py" -Encoding utf8
}

# Allow traffic on port 80 through the firewall
Write-Output "Allowing traffic on port 80 through the firewall..."
netsh advfirewall firewall add rule name="Allow Port 80" dir=in action=allow protocol=TCP localport=80

# Start the Flask application using gunicorn with increased timeout on port 80
Write-Output "Starting the Flask application using gunicorn..."
& .\venv\Scripts\gunicorn.exe --bind 0.0.0.0:80 wsgi:app --timeout 120 --log-level debug --access-logfile - --error-logfile -