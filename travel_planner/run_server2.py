# -*- coding: utf-8 -*-
import sys
import os
import traceback

sys.path.insert(0, r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')
os.chdir(r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')

try:
    os.environ['FLASK_APP'] = 'app'
    os.environ['FLASK_ENV'] = 'development'

    print("Step 1: Importing Flask...")
    from app import create_app
    
    print("Step 2: Creating app...")
    app = create_app('development')
    
    print("Step 3: Starting server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
    
except Exception as e:
    print(f"\n错误: {e}")
    traceback.print_exc()
    input("\n按回车键退出...")