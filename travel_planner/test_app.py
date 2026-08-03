# -*- coding: utf-8 -*-
import sys
import traceback

print("=" * 60)
print("Testing Travel Planner Application")
print("=" * 60)
print()

try:
    print("[1/8] Importing Flask...")
    from flask import Flask
    print("       SUCCESS")
    print()
    
    print("[2/8] Importing config...")
    from config import config
    print("       SUCCESS")
    print()
    
    print("[3/8] Importing extensions...")
    from app.extensions import db, login_manager, csrf, migrate, init_redis
    print("       SUCCESS")
    print()
    
    print("[4/8] Creating Flask app...")
    app = Flask(__name__)
    print("       SUCCESS")
    print()
    
    print("[5/8] Loading configuration...")
    app.config.from_object(config['development'])
    print("       SUCCESS")
    print()
    
    print("[6/8] Initializing extensions...")
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    init_redis(app)
    print("       SUCCESS")
    print()
    
    print("[7/8] Registering blueprints...")
    from app.blueprints.auth import auth_bp
    from app.blueprints.destinations import destinations_bp
    from app.blueprints.itineraries import itineraries_bp
    from app.blueprints.community import community_bp
    from app.blueprints.ai import ai_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(destinations_bp, url_prefix='/destinations')
    app.register_blueprint(itineraries_bp, url_prefix='/itineraries')
    app.register_blueprint(community_bp, url_prefix='/community')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    print("       SUCCESS")
    print()
    
    print("[8/8] Initializing services...")
    from app.services.ai_service import init_ai_service
    from app.services.weather_service import init_weather_service
    from app.services.pdf_service import init_pdf_service
    
    init_ai_service()
    init_weather_service()
    init_pdf_service(app)
    print("       SUCCESS")
    print()
    
    print("=" * 60)
    print("All tests passed! Application can be started.")
    print("=" * 60)
    print()
    print("To start the server, run:")
    print("  venv\\Scripts\\python.exe run.py")
    print()
    
except Exception as e:
    print()
    print("=" * 60)
    print("ERROR: Application failed to initialize")
    print("=" * 60)
    print(f"Error: {e}")
    print()
    traceback.print_exc()
    sys.exit(1)