# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime

# 确保输出使用UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 重定向输出到文件
log_file_path = 'server_output.log'

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
        f.flush()
    print(line, flush=True)

log("=" * 60)
log("Starting Travel Planner Server")
log("=" * 60)

try:
    log("Importing create_app...")
    from app import create_app
    log("SUCCESS")
    
    log("Creating app...")
    app = create_app('development')
    log("App created successfully")
    
    log("")
    log("Starting server on http://127.0.0.1:5000")
    log("Press CTRL+C to stop")
    log("")
    log("=" * 60)
    
    # 启动服务器 - 使用threaded=True允许多个请求
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)
    
except KeyboardInterrupt:
    log("")
    log("Server stopped by user")
    sys.exit(0)
except Exception as e:
    log(f"ERROR: {e}")
    import traceback
    with open(log_file_path, 'a', encoding='utf-8') as f:
        traceback.print_exc(file=f)
    sys.exit(1)