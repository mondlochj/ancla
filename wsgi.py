"""
WSGI entry point for production deployment with Apache/mod_wsgi
"""
from app import create_app

application = create_app('production')
