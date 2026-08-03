import sys
import os

# 设置路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    print('Import success')
    
    app = create_app('development')
    print('App created')
    
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
    input('Press Enter to exit')
