# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')

try:
    print("Step 1: Setting environment...")
    os.environ['FLASK_APP'] = 'app'
    os.environ['FLASK_ENV'] = 'development'
    
    print("Step 2: Importing create_app...")
    from app import create_app
    
    print("Step 3: Creating app...")
    app = create_app('development')
    
    print("Step 4: Checking routes...")
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
    
    print(f"Found {len(routes)} routes")
    
    print("Step 5: Starting server...")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")