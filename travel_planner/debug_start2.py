import os
import sys
import traceback

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

print("Step 1: Setting up environment")
print("CWD:", os.getcwd())
print("PYTHONPATH:", sys.path[:3])

try:
    print("\nStep 2: Importing create_app")
    from app import create_app
    print("OK")
    
    print("\nStep 3: Creating app instance")
    app = create_app('development')
    print("OK")
    
    print("\nStep 4: Checking configuration")
    print("Debug:", app.config.get('DEBUG'))
    print("Database:", app.config.get('SQLALCHEMY_DATABASE_URI'))
    
    print("\nStep 5: Testing database connection")
    with app.app_context():
        from app.extensions import db
        try:
            db.create_all()
            print("Database connection OK")
        except Exception as e:
            print("Database error:", str(e))
    
    print("\nStep 6: Starting server...")
    app.run(host='127.0.0.1', port=5000, debug=False)
    
except Exception as e:
    print("\nERROR:", str(e))
    traceback.print_exc()