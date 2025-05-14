#!/bin/bash

echo "--- Quick Setup Script for Linux/macOS (Non-Admin) ---"
echo "This script will check for Python, create a virtual environment, install Python dependencies,"
echo "and check for required command-line tools."
echo "It CANNOT install Python itself or system-wide tools if they are missing."
echo ""

# --- 1. Check for Python 3 ---
echo "[INFO] Checking for Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "[OK] Python 3 found as '$PYTHON_CMD'."
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "[WARNING] Found 'python'. Assuming it's Python 3. If not, issues may occur."
    # You might add a more specific version check here if needed
    # python -c 'import sys; sys.exit(0 if sys.version_info.major == 3 else 1)'
    # if [ $? -ne 0 ]; then
    #     echo "[ERROR] 'python' is not Python 3. Please install Python 3 and ensure 'python3' is in your PATH."
    #     exit 1
    # fi
else
    echo "[ERROR] Python 3 (as 'python3' or 'python') not found in PATH."
    echo "Please install Python 3 (e.g., from your system's package manager with sudo, or using pyenv for user-local install)."
    exit 1
fi

# --- 2. Create Virtual Environment (if it doesn't exist) ---
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Virtual environment '$VENV_DIR' not found. Creating..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        exit 1
    fi
    echo "[OK] Virtual environment created."
else
    echo "[OK] Virtual environment '$VENV_DIR' already exists."
fi

# --- 3. Install Dependencies from requirements.txt ---
REQUIREMENTS_FILE="requirements.txt"
PIP_CMD="$VENV_DIR/bin/pip"

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "[WARNING] '$REQUIREMENTS_FILE' not found. Creating a default one with Flask and Waitress."
    cat <<EOL > $REQUIREMENTS_FILE
Flask
waitress
EOL
fi

echo "[INFO] Installing dependencies from '$REQUIREMENTS_FILE' into '$VENV_DIR'..."
$PIP_CMD install -r "$REQUIREMENTS_FILE"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies using $PIP_CMD."
    echo "Make sure '$VENV_DIR' is a valid virtual environment and '$REQUIREMENTS_FILE' is correct."
    exit 1
fi
echo "[OK] Python dependencies installed successfully."

# --- 4. Check for Command-Line Tools ---
echo "[INFO] Checking for required command-line tools..."
MISSING_TOOLS=0
TOOLS_TO_CHECK=("nslookup" "ping" "dig" "traceroute")

for tool in "${TOOLS_TO_CHECK[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo "[OK] Found '$tool'."
    else
        echo "[WARNING] '$tool' NOT found in PATH."
        MISSING_TOOLS=$((MISSING_TOOLS + 1))
    fi
done

if [ $MISSING_TOOLS -ne 0 ]; then
    echo "[ALERT] Some command-line tools are missing. The application may not function correctly."
    echo "You might need to install them (e.g., 'dnsutils' for nslookup/dig, 'iputils-ping', 'traceroute'). This may require sudo access."
else
    echo "[OK] All checked command-line tools seem to be available."
fi

echo ""
echo "--- Setup Verification Complete ---"
echo "To run the application:"
echo "1. Activate the virtual environment: source $VENV_DIR/bin/activate"
echo "2. Run the Python application: python app.py (or python3 app.py)"
echo " (Note: The modified app.py from previous suggestions can run directly using '$VENV_DIR/bin/python app.py' or after activation)"
echo ""
