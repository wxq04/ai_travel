@echo off
cd /d "c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner"
echo Starting server...
"venv\Scripts\python.exe" detailed_start.py > server_log.txt 2>&1
echo Server stopped. Check server_log.txt for details.