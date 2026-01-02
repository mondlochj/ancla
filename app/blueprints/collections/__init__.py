from flask import Blueprint

collections_bp = Blueprint('collections', __name__, template_folder='templates')

from . import routes
