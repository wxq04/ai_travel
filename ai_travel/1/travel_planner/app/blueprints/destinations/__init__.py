from flask import Blueprint

destinations_bp = Blueprint('destinations', __name__)

from app.blueprints.destinations import routes