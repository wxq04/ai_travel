#!/usr/bin/env python
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from app import create_app

app = create_app('development')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)