from flask import Flask, render_template, request
import subprocess
import platform

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    target = ''
    tool = 'nslookup'
    dig_type = 'A'

    if request.method == 'POST':
        target = request.form.get('target-name')
        tool = request.form.get('tool-name')
        dig_type = request.form.get('dig-type')

        # Process the command based on the tool and target
        if tool == 'nslookup':
            result = run_nslookup(target)
        elif tool == 'ping':
            result = run_ping(target)
        elif tool == 'dig':
            result = run_dig(target, dig_type)
        elif tool == 'traceroute':
            result = run_traceroute(target)

    return render_template('index.html', result=result, target=target, tool=tool, dig_type=dig_type)

def run_nslookup(target):
    try:
        # Sanitize input to prevent command injection
        if not target or not target.replace('.', '').isalnum():
            return "Invalid input. Please use alphanumeric characters and dots."
        return subprocess.check_output(['nslookup', target], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def run_ping(target):
    try:
        # Sanitize input to prevent command injection
        if not target or not target.replace('.', '').isalnum():
            return "Invalid input. Please use alphanumeric characters and dots."
        return subprocess.check_output(['ping', '-c', '4', target], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def run_dig(target, dig_type):
    try:
        # Sanitize input to prevent command injection
        if not target or not target.replace('.', '').isalnum():
            return "Invalid input. Please use alphanumeric characters and dots."
        return subprocess.check_output(['dig', target, dig_type], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def run_traceroute(target):
    try:
        # Sanitize input to prevent command injection
        if not target or not target.replace('.', '').isalnum():
            return "Invalid input. Please use alphanumeric characters and dots."
        if platform.system().lower() == "windows":
            return subprocess.check_output(['tracert', target], stderr=subprocess.STDOUT, universal_newlines=True)
        else:
            return subprocess.check_output(['traceroute', target], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.output}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)