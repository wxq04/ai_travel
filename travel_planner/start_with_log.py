# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime

# 重定向输出到文件
log_file = open('startup.log', 'w', encoding='utf-8')

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}\n"
    log_file.write(line)
    log_file.flush()
    print(line, end='')

log("=" * 60)
log("Travel Planner AI - Starting Server")
log("=" * 60)

try:
    log("Importing application modules...")
    from app import create_app
    log("SUCCESS: Modules imported")
    
    log("Creating Flask application...")
    app = create_app('development')
    log("SUCCESS: Application created")
    
    log("")
    log("Starting Flask development server...")
    log("Server address: http://0.0.0.0:5000")
    log("Press CTRL+C to stop")
    log("")
    
    # 关闭日志文件
    log_file.close()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    
except Exception as e:
    log(f"ERROR: {e}")
    import traceback
    traceback.print_exc(file=log_file)
    log_file.close()
    input("Press Enter to exit...")
