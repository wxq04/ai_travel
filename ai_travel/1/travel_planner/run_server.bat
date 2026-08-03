@echo off
set "BASE_DIR=c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner"
cd /d "%BASE_DIR%"
set "PYTHONPATH=%BASE_DIR%"
call venv\Scripts\activate.bat
python -c "from app import create_app; app = create_app('development'); app.run(host='127.0.0.1', port=5000, debug=False)"