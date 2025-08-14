from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import sys
import time

app = Flask(__name__)

def execute_python_code(code, timeout=30):
    result = {
        "success": False,
        "output": "",
        "error": "",
        "execution_time": 0
    }
    
    start_time = time.time()
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        process = subprocess.Popen(
            [sys.executable, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        
        stdout, stderr = process.communicate(timeout=timeout)
        execution_time = time.time() - start_time
        result["execution_time"] = round(execution_time, 3)
        
        if process.returncode == 0:
            result["success"] = True
            result["output"] = stdout
        else:
            result["success"] = False
            result["error"] = stderr if stderr else f"Process exited with code {process.returncode}"
            result["output"] = stdout
            
    except subprocess.TimeoutExpired:
        process.kill()
        result["error"] = f"Code execution timed out after {timeout} seconds"
        result["execution_time"] = timeout
    except Exception as e:
        result["error"] = str(e)
        result["execution_time"] = time.time() - start_time
    finally:
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass
    
    return result

@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    
    if not data or not data.get('code'):
        return jsonify({"success": False, "error": "No code provided"}), 400
    
    code = data.get('code')
    timeout = min(data.get('timeout', 30), 60)
    
    result = execute_python_code(code, timeout)
    status_code = 200 if result["success"] else 400
    
    return jsonify(result), status_code

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
