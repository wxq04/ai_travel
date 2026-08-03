# -*- coding: utf-8 -*-
from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Travel Planner with Waitress!"

print("Starting server with waitress...")
print("Testing on port 5002")
serve(app, host='127.0.0.1', port=5002)