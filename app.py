from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import sys
import time
import threading
import uuid
from datetime import datetime

app = Flask(__name__)

# In-memory storage for job results (use Redis/database in production)
jobs = {}

def execute_python_code_async(job_id, code):
    """Execute code asynchronously and store results"""
    result = {
        "status": "running",
        "success": False,
        "output": "",
        "error": "",
        "execution_time": 0,
        "started_at": datetime.now().isoformat()
    }
    
    jobs[job_id] = result
    start_time = time.time()
    
    try:
        # Quick syntax check first
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            jobs[job_id].update({
                "status": "failed",
                "success": False,
                "error": f"Syntax Error: {str(e)}",
                "execution_time": time.time() - start_time,
                "completed_at": datetime.now().isoformat()
            })
            return
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        # Update status to indicate code is syntactically valid and running
        jobs[job_id]["status"] = "executing"
        
        process = subprocess.Popen(
            [sys.executable, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        execution_time = time.time() - start_time
        
        if process.returncode == 0:
            jobs[job_id].update({
                "status": "completed",
                "success": True,
                "output": stdout,
                "execution_time": round(execution_time, 3),
                "completed_at": datetime.now().isoformat()
            })
        else:
            jobs[job_id].update({
                "status": "failed",
                "success": False,
                "error": stderr if stderr else f"Process exited with code {process.returncode}",
                "output": stdout,
                "execution_time": round(execution_time, 3),
                "completed_at": datetime.now().isoformat()
            })
            
    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "success": False,
            "error": str(e),
            "execution_time": time.time() - start_time,
            "completed_at": datetime.now().isoformat()
        })
    finally:
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass

@app.route('/run', methods=['POST'])
def start_execution():
    """Start code execution and return job ID immediately"""
    data = request.get_json()
    
    if not data or not data.get('code'):
        return jsonify({"success": False, "error": "No code provided"}), 400
    
    code = data.get('code')
    job_id = str(uuid.uuid4())
    
    # Start execution in background thread
    thread = threading.Thread(target=execute_python_code_async, args=(job_id, code))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "job_id": job_id,
        "status": "started",
        "message": "Code execution started. Use /status/{job_id} to check progress."
    }), 202

@app.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get the status and results of a job"""
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(jobs[job_id])

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs (optional - for debugging)"""
    return jsonify({
        "jobs": list(jobs.keys()),
        "total": len(jobs)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
