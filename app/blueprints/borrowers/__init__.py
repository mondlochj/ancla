from flask import Blueprint

borrowers_bp = Blueprint('borrowers', __name__, template_folder='templates')

from . import routes
