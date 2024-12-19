from flask import Flask, render_template, request, session
import subprocess
import platform
import os
import logging
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        target = request.form.get('target-name')
        tool = request.form.get('tool-name')
        dig_type = request.form.get('dig-type')

        # Store user-specific data in the session
        session['target'] = target
        session['tool'] = tool
        session['dig_type'] = dig_type

        # Process the command based on the tool and target
        if tool == 'nslookup':
            result = run_nslookup(target)
        elif tool == 'ping':
            result = run_ping(target)
        elif tool == 'dig':
            result = run_dig(target, dig_type)
        elif tool == 'traceroute':
            result = run_traceroute(target)

        # Store the result in the session
        session['result'] = result

    return render_template('index.html', result=session.get('result'), target=session.get('target', ''), tool=session.get('tool', 'nslookup'), dig_type=session.get('dig_type', 'A'))

def is_valid_target(target):
    # Allow alphanumeric characters, dots, hyphens, and underscores
    return all(c.isalnum() or c in ('.', '-', '_') for c in target)

def run_nslookup(target):
    try:
        logging.debug(f"Running nslookup for target: {target}")
        # Sanitize input to prevent command injection
        if not target or not is_valid_target(target):
            return "Invalid input. Please use alphanumeric characters, dots, hyphens, and underscores."
        result = subprocess.check_output(['nslookup', target], stderr=subprocess.STDOUT, universal_newlines=True)
        logging.debug(f"nslookup result: {result}")
        return result
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def run_ping(target):
    try:
        logging.debug(f"Running ping for target: {target}")
        # Sanitize input to prevent command injection
        if not target or not is_valid_target(target):
            return "Invalid input. Please use alphanumeric characters, dots, hyphens, and underscores."
        if platform.system().lower() == "windows":
            result = subprocess.check_output(['ping', target], stderr=subprocess.STDOUT, universal_newlines=True)
        else:
            result = subprocess.check_output(['ping', '-c', '4', target], stderr=subprocess.STDOUT, universal_newlines=True)
        logging.debug(f"ping result: {result}")
        return result
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def run_dig(target, dig_type):
    try:
        logging.debug(f"Running dig for target: {target} with type: {dig_type}")
        # Sanitize input to prevent command injection
        if not target or not is_valid_target(target):
            return "Invalid input. Please use alphanumeric characters, dots, hyphens, and underscores."
        
        if platform.system().lower() == "windows":
            # Run dig through WSL on Windows
            result = subprocess.check_output(['wsl', 'dig', target, dig_type], stderr=subprocess.STDOUT, universal_newlines=True)
        else:
            # Run dig directly on Linux
            result = subprocess.check_output(['dig', target, dig_type], stderr=subprocess.STDOUT, universal_newlines=True)
        
        logging.debug(f"dig result: {result}")
        return result
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def run_traceroute(target):
    try:
        logging.debug(f"Running traceroute for target: {target}")
        # Sanitize input to prevent command injection
        if not target or not is_valid_target(target):
            return "Invalid input. Please use alphanumeric characters, dots, hyphens, and underscores."
        
        command = ['tracert', target] if platform.system().lower() == "windows" else ['traceroute', target]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        def kill_process_after_timeout(p, timeout):
            try:
                p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                p.kill()
        
        timeout_thread = threading.Thread(target=kill_process_after_timeout, args=(process, 10))
        timeout_thread.start()
        timeout_thread.join()
        
        stdout, stderr = process.communicate()
        logging.debug(f"traceroute result: {stdout}")
        return stdout if stdout else f"Command failed: {stderr}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=80, threads=4)  # Use 4 threads for handling requests