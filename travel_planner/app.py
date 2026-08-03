import os
import sys

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from app import create_app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='127.0.0.1', port=5000, debug=False)