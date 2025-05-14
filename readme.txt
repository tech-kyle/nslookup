# nslookup

## Description
How to Use:

1. Save the appropriate script (e.g., quick_setup_linux_mac.sh or quick_setup_windows.ps1) in the same directory as your app.py and requirements.txt.
2. Make the script executable (for Linux/macOS): chmod +x quick_setup_linux_mac.sh
3. Run the script:
    Linux/macOS: ./quick_setup_linux_mac.sh
    Windows (PowerShell): .\quick_setup_windows.ps1 (You might need to adjust PowerShell execution policy: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass for the current session if it's restricted).
4. Follow any instructions or warnings the script provides.
5. Once the script completes successfully, you can follow its output instructions to activate the virtual environment and run python app.py.
6. Open your web browser and go to `http://localhost:8080`. The web interface will allow you to perform the `nslookup`, `dig`, and `ping` commands.


Important Limitations (No Admin/Sudo Rights):
These scripts cannot:
1. Install Python itself if it's missing from the system. - Python3
2. Install system-wide command-line tools like nslookup, dig, traceroute, or enable system features like WSL if they require admin/sudo privileges.

