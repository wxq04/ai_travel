# -*- coding: utf-8 -*-
from app import create_app
import os

os.environ['WERKZEUG_RUN_MAIN'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

app = create_app('development')

if __name__ == '__main__':
    print("=" * 60)
    print("Travel Planner AI")
    print("=" * 60)
    print("Server starting on http://127.0.0.1:5000")
    print("Press CTRL+C to stop")
    print()
    
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)