from flask import Blueprint

attractions_bp = Blueprint('attractions', __name__, template_folder='../../templates/attractions')

from . import routes
