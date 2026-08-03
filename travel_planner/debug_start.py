import os
import sys
import traceback

os.chdir(r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')
sys.path.insert(0, os.getcwd())

print("Step 1: Import create_app")
try:
    from app import create_app
    print("OK")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 2: Create app")
try:
    app = create_app('development')
    print("OK")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: List all routes")
try:
    routes = list(app.url_map.iter_rules())
    print(f"Total routes: {len(routes)}")
    for route in routes:
        print(f"  {route}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

print("\nStep 4: Start server")
try:
    app.run(host='127.0.0.1', port=5000, debug=False)
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()