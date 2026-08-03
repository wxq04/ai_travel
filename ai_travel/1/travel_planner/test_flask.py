# -*- coding: utf-8 -*-
import sys

try:
    print("Step 1: Import Flask...", flush=True)
    from flask import Flask
    print("Step 2: Create test app...", flush=True)
    test_app = Flask(__name__)
    
    @test_app.route('/')
    def hello():
        return "Hello from Travel Planner!"
    
    print("Step 3: Run test app...", flush=True)
    test_app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")