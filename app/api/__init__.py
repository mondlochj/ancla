"""
Ancla Capital REST API Blueprint

This module provides REST API endpoints for the React frontend.
All endpoints are prefixed with /api/.
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes to register them
from . import auth, dashboard, loans, borrowers, properties, payments, collections, documents
