from flask import Flask, render_template, request
import subprocess
import platform

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def network_tools():
    result = None
    target = ""
    tool = ""
    dig_type = "A"  # Default dig type
    
    if request.method == 'POST':
        target = request.form['target']
        tool = request.form['tool']
        dig_type = request.form.get('dig_type', 'A')
        
        try:
            # Sanitize input to prevent command injection
            if not target or not target.replace('.', '').isalnum():
                result = "Invalid input. Please use alphanumeric characters and dots."
            else:
                # Execute the selected command
                if tool == 'nslookup':
                    result = subprocess.check_output(['nslookup', target], 
                                                     stderr=subprocess.STDOUT,
                                                     universal_newlines=True)
                elif tool == 'ping':
                    result = subprocess.check_output(['ping', '-c', '4', target], 
                                                     stderr=subprocess.STDOUT,
                                                     universal_newlines=True)
                elif tool == 'dig':
                    result = subprocess.check_output(['dig', target, dig_type], 
                                                     stderr=subprocess.STDOUT,
                                                     universal_newlines=True)
                elif tool == 'traceroute':
                    if platform.system().lower() == "windows":
                        result = subprocess.check_output(['tracert', target], 
                                                         stderr=subprocess.STDOUT,
                                                         universal_newlines=True)
                    else:
                        result = subprocess.check_output(['traceroute', target], 
                                                         stderr=subprocess.STDOUT,
                                                         universal_newlines=True)
        except subprocess.CalledProcessError as e:
            result = f"Command failed: {e.output}"
        except Exception as e:
            result = f"An error occurred: {str(e)}"
    
    return render_template('index.html', result=result, target=target, tool=tool, dig_type=dig_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)