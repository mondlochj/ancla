from flask import Blueprint

collateral_bp = Blueprint('collateral', __name__, template_folder='templates')

from . import routes
