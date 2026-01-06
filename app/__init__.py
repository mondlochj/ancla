import os
from datetime import timedelta
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import config
from .extensions import db, login_manager, bcrypt, csrf, migrate, jwt, cors


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']

    # Handle proxy headers from Apache
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload directories exist
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)

    # Register blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.borrowers import borrowers_bp
    from .blueprints.collateral import collateral_bp
    from .blueprints.loans import loans_bp
    from .blueprints.legal import legal_bp
    from .blueprints.payments import payments_bp
    from .blueprints.collections import collections_bp
    from .blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(borrowers_bp, url_prefix='/borrowers')
    app.register_blueprint(collateral_bp, url_prefix='/collateral')
    app.register_blueprint(loans_bp, url_prefix='/loans')
    app.register_blueprint(legal_bp, url_prefix='/legal')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(collections_bp, url_prefix='/collections')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Register API blueprint (exempt from CSRF for JWT auth)
    from .api import api_bp
    csrf.exempt(api_bp)
    app.register_blueprint(api_bp)

    # User loader for Flask-Login
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Context processor for templates
    @app.context_processor
    def utility_processor():
        from .models.user import RoleName
        from datetime import datetime
        return {
            'RoleName': RoleName,
            'now': datetime.utcnow
        }

    # Root redirect
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role.name == 'Borrower':
                return redirect(url_for('loans.my_loans'))
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.login'))

    # Register CLI commands
    from .cli import register_cli_commands
    register_cli_commands(app)

    return app
