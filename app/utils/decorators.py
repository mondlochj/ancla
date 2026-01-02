from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def role_required(*role_names):
    """Decorator to require specific roles for a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))

            if not current_user.has_role(*role_names):
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_admin():
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def verified_required(f):
    """Decorator to require email verification."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_verified:
            flash('Please verify your email address to access this feature.', 'warning')
            return redirect(url_for('auth.unverified'))

        return f(*args, **kwargs)
    return decorated_function


def permission_required(resource, action):
    """Decorator to require specific permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))

            if not current_user.can(resource, action):
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def internal_only(f):
    """Decorator to restrict access to internal users (not borrowers)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        from ..models.user import RoleName
        if current_user.role.name == RoleName.BORROWER.value:
            abort(403)

        return f(*args, **kwargs)
    return decorated_function
