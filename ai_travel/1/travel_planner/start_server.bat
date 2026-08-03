@echo off
cd /d "c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner"
"venv\Scripts\python.exe" -c "
import sys
sys.path.insert(0, r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')
try:
    from app import create_app
    app = create_app('development')
    print('App created successfully')
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
    input('Press Enter...')
" > server_output.log 2>&1