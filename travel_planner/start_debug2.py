import os
import sys

print("Step 1: Set environment")
os.chdir(r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')
sys.path.insert(0, os.getcwd())
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

print("\nStep 2: Import create_app")
from app import create_app
print("Import successful")

print("\nStep 3: Create app")
try:
    app = create_app('development')
    print("App created successfully")
    print(f"DEBUG: {app.debug}")
    print(f"SECRET_KEY set: {len(app.config.get('SECRET_KEY', '')) > 0}")
except Exception as e:
    print(f"Error creating app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 4: List routes")
routes = list(app.url_map.iter_rules())
print(f"Found {len(routes)} routes")
for route in routes[:5]:
    print(f"  {route}")

print("\nStep 5: Start server")
try:
    app.run(host='127.0.0.1', port=5000, debug=False)
except Exception as e:
    print(f"Error running server: {e}")
    import traceback
    traceback.print_exc()