from flask import Blueprint

ai_bp = Blueprint('ai', __name__)

from app.blueprints.ai import routes