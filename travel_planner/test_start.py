import os
import sys

os.chdir(r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')
sys.path.insert(0, os.getcwd())

print("Starting test...")

try:
    print("Importing create_app...")
    from app import create_app
    print("Import OK")
    
    print("Creating app...")
    app = create_app('development')
    print("App created")
    
    print("Checking routes...")
    routes = list(app.url_map.iter_rules())
    print("Total routes:", len(routes))
    
    for route in routes:
        if 'save' in str(route):
            print("Save route found:", route)
    
    print("Starting server...")
    app.run(host='127.0.0.1', port=5000, debug=False)
    
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()