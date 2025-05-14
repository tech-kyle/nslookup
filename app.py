from flask import Flask, render_template, request, session
import subprocess
import platform
import os
import sys # Needed for sys.executable and sys.exit
import logging

# --- Your existing Flask app definition and routes ---
# (Keep app = Flask(__name__), @app.route(...), helper functions like
#  run_nslookup, run_ping, run_dig, run_traceroute as they are)
# Make sure to adjust the port in the final serve() call if it was 80.

app = Flask(__name__)
app.secret_key = os.urandom(24)
logging.basicConfig(level=logging.DEBUG)

# (Your existing route and helper functions: index, is_valid_target, run_nslookup, run_ping, run_dig, run_traceroute)
# These functions already handle OS differences for commands correctly.
# For example:
# def run_ping(target):
#     # ...
#     if platform.system().lower() == "windows":
#         command = ['ping', target]
#     else:
#         command = ['ping', '-c', '4', target]
#     # ...
# (Ensure all such helper functions are included from your original app.py)
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        target = request.form.get('target-name')
        tool = request.form.get('tool-name')
        dig_type = request.form.get('dig-type')
        session['target'] = target
        session['tool'] = tool
        session['dig_type'] = dig_type
        if tool == 'nslookup':
            result = run_nslookup(target)
        elif tool == 'ping':
            result = run_ping(target)
        elif tool == 'dig':
            result = run_dig(target, dig_type)
        elif tool == 'traceroute':
            result = run_traceroute(target)
        session['result'] = result
    return render_template('index.html', result=session.get('result'), target=session.get('target', ''), tool=session.get('tool', 'nslookup'), dig_type=session.get('dig_type', 'A'))

def is_valid_target(target):
    return all(c.isalnum() or c in ('.', '-', '_') for c in target)

def run_nslookup(target):
    try:
        logging.debug(f"Running nslookup for target: {target}")
        if not target or not is_valid_target(target):
            return "Invalid input."
        result = subprocess.check_output(['nslookup', target], stderr=subprocess.STDOUT, universal_newlines=True, timeout=10)
        logging.debug(f"nslookup result: {result}")
        return result
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 10 seconds."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def run_ping(target):
    try:
        logging.debug(f"Running ping for target: {target}")
        if not target or not is_valid_target(target):
            return "Invalid input."
        if platform.system().lower() == "windows":
            result = subprocess.check_output(['ping', target], stderr=subprocess.STDOUT, universal_newlines=True, timeout=10)
        else:
            result = subprocess.check_output(['ping', '-c', '4', target], stderr=subprocess.STDOUT, universal_newlines=True, timeout=10)
        logging.debug(f"ping result: {result}")
        return result
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 10 seconds."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def run_dig(target, dig_type):
    try:
        logging.debug(f"Running dig for target: {target} with type: {dig_type}")
        if not target or not is_valid_target(target):
            return "Invalid input."
        command = ['dig', target, dig_type]
        if platform.system().lower() == "windows":
            command.insert(0, 'wsl') # Prepend 'wsl' for windows
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, timeout=15)
        logging.debug(f"dig result: {result}")
        return result
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 15 seconds."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def run_traceroute(target):
    try:
        logging.debug(f"Running traceroute for target: {target}")
        if not target or not is_valid_target(target):
            return "Invalid input."
        command = ['tracert', target] if platform.system().lower() == "windows" else ['traceroute', target]
        # Using a longer timeout for traceroute as it can be slow
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        try:
            stdout, stderr = process.communicate(timeout=30) # 30 second timeout
            if process.returncode != 0:
                 # Combine stdout and stderr for error messages if command failed
                error_output = stdout + stderr
                return f"Command failed or produced error: {error_output.strip()}"
            logging.debug(f"traceroute result: {stdout}")
            return stdout
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return f"Traceroute command timed out after 30 seconds. Partial output:\n{stdout}{stderr}"
    except Exception as e:
        return f"An error occurred during traceroute: {str(e)}"


# --- New Setup and Run Logic ---
def setup_and_run():
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    VENV_DIR = os.path.join(PROJECT_DIR, "venv")
    REQUIREMENTS_FILE = os.path.join(PROJECT_DIR, "requirements.txt")
    PORT = 8080  # Non-privileged port

    # Determine python and pip executables
    if platform.system() == "Windows":
        python_executable = os.path.join(VENV_DIR, "Scripts", "python.exe")
        pip_executable = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        python_executable = os.path.join(VENV_DIR, "bin", "python")
        pip_executable = os.path.join(VENV_DIR, "bin", "pip")

    # 1. Check for virtual environment
    if not os.path.exists(VENV_DIR):
        print(f"Virtual environment not found at {VENV_DIR}")
        print("Attempting to create virtual environment...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
            print(f"Virtual environment created at {VENV_DIR}")
            print("Please re-run the script to install dependencies and start the application.")
            sys.exit(0) # Exit so user can re-run to use the new venv
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            print(f"Please create it manually: {sys.executable} -m venv {VENV_DIR}")
            sys.exit(1)

    # 2. Ensure dependencies are installed using pip from the virtual environment
    print("Checking and installing dependencies...")
    try:
        # Ensure requirements.txt exists
        if not os.path.exists(REQUIREMENTS_FILE):
            print(f"Error: '{REQUIREMENTS_FILE}' not found. Cannot install dependencies.")
            # Create a basic one if it's missing and only Flask is the core dep for app.py
            with open(REQUIREMENTS_FILE, "w") as f:
                f.write("Flask\n")
                f.write("waitress\n") # Add waitress
            print(f"Created a basic '{REQUIREMENTS_FILE}'. Please verify its contents.")

        subprocess.check_call([pip_executable, "install", "-r", REQUIREMENTS_FILE])
        # Explicitly ensure waitress is installed as it's used to serve
        subprocess.check_call([pip_executable, "install", "waitress"])
        print("Dependencies are up to date.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies using '{pip_executable}': {e}")
        print(f"Make sure the virtual environment at '{VENV_DIR}' is correctly set up and '{REQUIREMENTS_FILE}' is valid.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Pip executable not found at '{pip_executable}'.")
        print(f"The virtual environment at '{VENV_DIR}' might not have been set up correctly or activated.")
        print(f"Try creating/recreating the venv: {sys.executable} -m venv {VENV_DIR} and re-run.")
        sys.exit(1)

    # 3. Run the Flask application using Waitress
    print(f"Starting Flask application on http://0.0.0.0:{PORT} using Waitress...")
    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=PORT, threads=4)
    except ImportError:
        print("Error: Waitress not found. It should have been installed from requirements.")
        print(f"Try installing it manually in your venv: {pip_executable} install waitress")
        sys.exit(1)

if __name__ == '__main__':
    setup_and_run()
