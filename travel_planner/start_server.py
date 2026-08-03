#!/usr/bin/env python
import os
import sys

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

print("Starting travel planner server...")
print("Working directory:", os.getcwd())

try:
    from app import create_app
    
    app = create_app('development')
    
    print("App created successfully")
    print("Routes:", [str(rule) for rule in app.url_map.iter_rules() if 'save' in str(rule)])
    
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")