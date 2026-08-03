#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

from app import create_app

app = create_app('development')
app.run(host='127.0.0.1', port=5000, debug=False)