import os
import sys
import traceback

os.chdir(r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')
sys.path.insert(0, os.getcwd())

print("=== Starting Server Debug ===")
print("Python:", sys.version)
print("CWD:", os.getcwd())

try:
    print("\n1. Importing create_app...")
    from app import create_app
    print("   ✓ Import successful")
    
    print("\n2. Creating app...")
    app = create_app('development')
    print("   ✓ App created")
    
    print("\n3. Checking routes...")
    routes = list(app.url_map.iter_rules())
    print(f"   ✓ Found {len(routes)} routes")
    
    # 检查save路由是否存在
    save_route = None
    for route in routes:
        if 'save' in str(route):
            save_route = route
            break
    
    if save_route:
        print(f"   ✓ Save route found: {save_route}")
    else:
        print("   ✗ Save route NOT found!")
    
    print("\n4. Starting server on http://127.0.0.1:5000...")
    app.run(host='127.0.0.1', port=5000, debug=False)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")