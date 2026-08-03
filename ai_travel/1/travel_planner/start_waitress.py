# -*- coding: utf-8 -*-
from app import create_app
from waitress import serve
import os

# 设置环境变量
os.environ['WERKZEUG_SUPPORT'] = 'true'

app = create_app('development')

print("=" * 60)
print("Travel Planner AI - AI 旅游行程规划助手")
print("=" * 60)
print()
print("Starting server on http://127.0.0.1:5000")
print("Press CTRL+C to stop")
print()

# 使用 waitress 服务器
serve(app, host='0.0.0.0', port=5000)