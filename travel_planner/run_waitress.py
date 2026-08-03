# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')

from app import create_app
from waitress import serve

print("正在启动服务器...")
print("请访问: http://127.0.0.1:5000")

app = create_app('development')
serve(app, host='127.0.0.1', port=5000, threads=4)