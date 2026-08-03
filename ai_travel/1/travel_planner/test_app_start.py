# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, 'c:\\Users\\Administrator\\Downloads\\智能系统作业\\期末作业\\travel_planner')

try:
    from app import create_app
    print("Import successful")
    
    app = create_app('development')
    print("App created successfully")
    
    print("Config:", app.config['SQLALCHEMY_DATABASE_URI'])
    
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()