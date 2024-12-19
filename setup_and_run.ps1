# Ensure script is run as Administrator
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Warning "You do not have Administrator rights to run this script!`nPlease re-run this script as an Administrator."
    exit
}

# Install Python using Chocolatey if not already installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Output "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Install Python using Chocolatey
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
pip install flask gunicorn waitress

# Allow traffic on port 80 through the firewall
Write-Output "Allowing traffic on port 80 through the firewall..."
netsh advfirewall firewall add rule name="Allow Port 80" dir=in action=allow protocol=TCP localport=80

# Start the Flask application using Gunicorn with multiple workers
Write-Output "Starting the Flask application using Gunicorn with multiple workers..."
& .\venv\Scripts\gunicorn.exe -b 0.0.0.0:80 app:app --worker-class=gevent --workers=4