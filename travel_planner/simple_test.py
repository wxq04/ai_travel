import os
import sys

os.chdir(r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')
sys.path.insert(0, os.getcwd())

# 先测试基础导入
try:
    print("Test 1: Import Flask")
    from flask import Flask
    print("OK")
except Exception as e:
    print("FAIL:", str(e))

try:
    print("Test 2: Import config")
    from config import config
    print("OK")
except Exception as e:
    print("FAIL:", str(e))

try:
    print("Test 3: Import extensions")
    from app.extensions import db, login_manager, csrf, migrate
    print("OK")
except Exception as e:
    print("FAIL:", str(e))

try:
    print("Test 4: Import create_app")
    from app import create_app
    print("OK")
except Exception as e:
    print("FAIL:", str(e))
    import traceback
    traceback.print_exc()