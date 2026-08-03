from flask import Blueprint

itineraries_bp = Blueprint('itineraries', __name__)

from app.blueprints.itineraries import routes