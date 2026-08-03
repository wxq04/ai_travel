import sys
import os

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("Working directory:", os.getcwd())

sys.path.insert(0, os.getcwd())

from app import create_app
app = create_app('development')
app.run(host='127.0.0.1', port=5000, debug=False)