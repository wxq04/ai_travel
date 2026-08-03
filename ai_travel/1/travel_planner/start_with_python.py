# -*- coding: utf-8 -*-
import subprocess
import time
import os

os.chdir(r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')

print("Starting Travel Planner server...")
print("=" * 60)

# 启动 waitress
process = subprocess.Popen(
    [r'venv\Scripts\waitress-serve.exe', 
     '--host=0.0.0.0', '--port=5000', '--threads=4',
     'app:create_app'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# 等待启动
time.sleep(3)

# 检查是否启动成功
if process.poll() is None:
    print("Server started successfully!")
    print("Access: http://127.0.0.1:5000")
    print("=" * 60)
    
    # 保持脚本运行
    while True:
        time.sleep(1)
else:
    print("Server failed to start")
    output = process.stdout.read()
    print(output)