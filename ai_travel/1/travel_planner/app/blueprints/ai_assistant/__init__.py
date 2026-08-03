from flask import Blueprint

ai_assistant_bp = Blueprint('ai_assistant', __name__, template_folder='../../templates/ai_assistant')

from . import routes
