import subprocess
import os
import sys

env = os.environ.copy()
env['PYTHONPATH'] = r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner'

cmd = [
    r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner\venv\Scripts\python.exe',
    '-c',
    'import sys; print("Python:", sys.version); from app import create_app; app = create_app("development"); print("App created"); app.run(host="127.0.0.1", port=5000, debug=False)'
]

print("Command:", " ".join(cmd))
print("Environment:", env.get('PYTHONPATH'))

try:
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=10)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
except subprocess.TimeoutExpired:
    print("Server started successfully (timeout)")
except Exception as e:
    print("Error:", str(e))