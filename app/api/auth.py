"""
Authentication API endpoints.

Provides JWT-based authentication for the React frontend.
"""

from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from marshmallow import ValidationError

from . import api_bp
from app.extensions import db, bcrypt
from app.models import User, Role
from app.schemas import UserSchema, LoginSchema, RegisterSchema, AuthResponseSchema


user_schema = UserSchema()


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT tokens."""
    try:
        data = LoginSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400

    user = User.query.filter_by(email=data['email'].lower()).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Create tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'user': user_schema.dump(user),
        'accessToken': access_token,
        'refreshToken': refresh_token,
    }), 200


@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user account."""
    try:
        json_data = request.get_json()
        # Add password to context for validation
        schema = RegisterSchema()
        schema.context = {'password': json_data.get('password')}
        data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400

    # Check if email exists
    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'message': 'Email already registered'}), 409

    # Get borrower role for new users
    borrower_role = Role.query.filter_by(name='Borrower').first()
    if not borrower_role:
        return jsonify({'message': 'System configuration error'}), 500

    # Create user
    user = User(
        email=data['email'].lower(),
        full_name=data['fullName'],
        password_hash=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
        role_id=borrower_role.id,
        is_verified=False,
    )
    db.session.add(user)
    db.session.commit()

    # Create tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'user': user_schema.dump(user),
        'accessToken': access_token,
        'refreshToken': refresh_token,
    }), 201


@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh the access token using a valid refresh token."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    return jsonify({'accessToken': access_token}), 200


@api_bp.route('/auth/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    """Invalidate the current tokens."""
    # In a production app, you'd add the token to a blocklist
    return jsonify({'message': 'Logged out successfully'}), 200


@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get the currently authenticated user's profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(user_schema.dump(user)), 200


@api_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Request a password reset email."""
    data = request.get_json()
    email = data.get('email', '').lower()

    # Always return success to prevent email enumeration
    user = User.query.filter_by(email=email).first()
    if user:
        # TODO: Generate reset token and send email
        pass

    return jsonify({'message': 'If an account exists, a reset email has been sent'}), 200


@api_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using a valid reset token."""
    data = request.get_json()
    token = data.get('token')
    password = data.get('password')

    if not token or not password:
        return jsonify({'message': 'Token and password are required'}), 400

    # TODO: Validate token and reset password
    return jsonify({'message': 'Password reset functionality coming soon'}), 501
