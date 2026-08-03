import sys
import os

print("Python version:", sys.version)
print("Current directory:", os.getcwd())

# 设置路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print("Python path:", sys.path[:3])

try:
    print("Importing create_app...")
    from app import create_app
    print("Import success")
    
    print("Creating app...")
    app = create_app('development')
    print("App created successfully")
    print("App config:", list(app.config.keys())[:10])
    
    print("Starting server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
