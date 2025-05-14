Write-Host "--- Quick Setup Script for Windows (Non-Admin) ---"
Write-Host "This script will check for Python, create a virtual environment, install Python dependencies,"
Write-Host "and check for required command-line tools."
Write-Host "It CANNOT install Python itself or system-wide tools if they are missing or require admin rights for setup (like WSL initial feature enablement)."
Write-Host ""

# --- 1. Check for Python 3 ---
Write-Host "[INFO] Checking for Python 3..."
$PythonExe = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonExe) {
    $PythonExe = Get-Command python3 -ErrorAction SilentlyContinue
}

if ($PythonExe) {
    $PYTHON_CMD = $PythonExe.Source
    Write-Host "[OK] Python found at '$PYTHON_CMD'."
    # Optional: Add version check
    # $pyVersion = Invoke-Expression "$PYTHON_CMD --version"
    # if ($pyVersion -notmatch "Python 3") {
    #     Write-Error "[ERROR] Detected Python is not Python 3 ($pyVersion). Please install Python 3."
    #     exit 1
    # }
} else {
    Write-Error "[ERROR] Python (as 'python' or 'python3') not found in PATH."
    Write-Host "Please install Python 3 (e.g., from python.org or the Microsoft Store)."
    exit 1
}

# --- 2. Create Virtual Environment (if it doesn't exist) ---
$VENV_DIR = "venv"
if (-not (Test-Path -Path $VENV_DIR -PathType Container)) {
    Write-Host "[INFO] Virtual environment '$VENV_DIR' not found. Creating..."
    Invoke-Expression "$PYTHON_CMD -m venv $VENV_DIR"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[ERROR] Failed to create virtual environment."
        exit 1
    }
    Write-Host "[OK] Virtual environment created."
} else {
    Write-Host "[OK] Virtual environment '$VENV_DIR' already exists."
}

# --- 3. Install Dependencies from requirements.txt ---
$REQUIREMENTS_FILE = "requirements.txt"
$PIP_CMD = Join-Path -Path $VENV_DIR -ChildPath "Scripts\pip.exe"

if (-not (Test-Path -Path $REQUIREMENTS_FILE)) {
    Write-Warning "[WARNING] '$REQUIREMENTS_FILE' not found. Creating a default one with Flask and Waitress."
    Set-Content -Path $REQUIREMENTS_FILE -Value "Flask`r`nwaitress"
}

Write-Host "[INFO] Installing dependencies from '$REQUIREMENTS_FILE' into '$VENV_DIR'..."
if (-not (Test-Path -Path $PIP_CMD)) {
    Write-Error "[ERROR] pip.exe not found at '$PIP_CMD'. The virtual environment might be corrupted or not created correctly."
    exit 1
}
Invoke-Expression "& `"$PIP_CMD`" install -r `"$REQUIREMENTS_FILE`""
if ($LASTEXITCODE -ne 0) {
    Write-Error "[ERROR] Failed to install dependencies using $PIP_CMD."
    Write-Host "Make sure '$VENV_DIR' is a valid virtual environment and '$REQUIREMENTS_FILE' is correct."
    exit 1
}
Write-Host "[OK] Python dependencies installed successfully."

# --- 4. Check for Command-Line Tools ---
Write-Host "[INFO] Checking for required command-line tools..."
$MissingTools = 0
$ToolsToCheck = @(
    @{ Name = "nslookup"; Command = "nslookup.exe" },
    @{ Name = "ping"; Command = "ping.exe" },
    @{ Name = "tracert"; Command = "tracert.exe" }
)

foreach ($toolInfo in $ToolsToCheck) {
    if (Get-Command $toolInfo.Command -ErrorAction SilentlyContinue) {
        Write-Host "[OK] Found '$($toolInfo.Name)'."
    } else {
        Write-Warning "[WARNING] '$($toolInfo.Name)' NOT found in PATH."
        $MissingTools++
    }
}

# Special check for 'dig' via WSL (as per your app.py)
Write-Host "[INFO] Checking for 'dig' via WSL..."
$wslCheck = Get-Command wsl -ErrorAction SilentlyContinue
if ($wslCheck) {
    Invoke-Expression "wsl which dig" -ErrorAction SilentlyContinue -OutVariable wslDigPath
    if ($LASTEXITCODE -eq 0 -and $wslDigPath) {
        Write-Host "[OK] Found 'dig' within WSL."
    } else {
        Write-Warning "[WARNING] 'dig' NOT found within WSL, or WSL is not configured to run it easily."
        Write-Host "         The app.py expects to run 'wsl dig ...'. Ensure WSL is installed, a Linux distro is set up, and 'dnsutils' (or similar providing dig) is installed within that distro."
        $MissingTools++
    }
} else {
    Write-Warning "[WARNING] WSL command ('wsl.exe') NOT found. 'dig' functionality via WSL will fail."
    $MissingTools++
}


if ($MissingTools -ne 0) {
    Write-Host "[ALERT] Some command-line tools are missing or not configured. The application may not function correctly."
    Write-Host "         For nslookup, ping, tracert: these are usually built into Windows. If missing, your Windows installation might have issues."
    Write-Host "         For dig via WSL: Ensure WSL feature is enabled, a Linux distro is installed (e.g., Ubuntu from MS Store), and 'dnsutils' package (or equivalent) is installed within that distro."
} else {
    Write-Host "[OK] All checked command-line tools seem to be available and configured."
}

Write-Host ""
Write-Host "--- Setup Verification Complete ---"
Write-Host "To run the application:"
Write-Host "1. Activate the virtual environment: & .\$VENV_DIR\Scripts\Activate.ps1"
Write-Host "2. Run the Python application: python app.py"
Write-Host " (Note: The modified app.py from previous suggestions can run directly using '.\$VENV_DIR\Scripts\python.exe app.py' or after activation)"
Write-Host ""
