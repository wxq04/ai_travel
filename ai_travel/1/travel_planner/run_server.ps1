$baseDir = "c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner"
Set-Location $baseDir
$env:PYTHONPATH = $baseDir
& "$baseDir\venv\Scripts\python.exe" -c "from app import create_app; app = create_app('development'); app.run(host='127.0.0.1', port=5000, debug=False)"