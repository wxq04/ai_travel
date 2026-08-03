import os
import sys

os.chdir(r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')
sys.path.insert(0, os.getcwd())

from app import create_app

app = create_app('development')
app.run(host='127.0.0.1', port=5000, debug=False)