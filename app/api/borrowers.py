"""
Borrowers API endpoints.

Provides CRUD operations for borrowers.
"""

from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_

from . import api_bp
from app.extensions import db
from app.models import Borrower, User, Loan
from app.schemas import BorrowerSchema, BorrowerCreateSchema, LoanSchema


borrower_schema = BorrowerSchema()
borrowers_schema = BorrowerSchema(many=True)
loans_schema = LoanSchema(many=True)


def check_internal_user():
    """Check if current user is an internal user (not borrower)."""
    user = User.query.get(get_jwt_identity())
    if not user or user.role.name == 'Borrower':
        return None
    return user


@api_bp.route('/borrowers', methods=['GET'])
@jwt_required()
def get_borrowers():
    """Get paginated list of borrowers with optional filters."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    verification_status = request.args.get('verificationStatus')
    risk_tier = request.args.get('riskTier')
    department = request.args.get('department')
    search = request.args.get('search', '')

    # Build query
    query = Borrower.query

    if verification_status:
        query = query.filter(Borrower.verification_status == verification_status)

    if risk_tier:
        query = query.filter(Borrower.risk_tier == risk_tier)

    if department:
        query = query.filter(Borrower.department == department)

    if search:
        query = query.filter(
            or_(
                Borrower.first_name.ilike(f'%{search}%'),
                Borrower.last_name.ilike(f'%{search}%'),
                Borrower.dpi.ilike(f'%{search}%'),
                Borrower.email.ilike(f'%{search}%'),
            )
        )

    # Order by name
    query = query.order_by(Borrower.last_name, Borrower.first_name)

    # Paginate
    total = query.count()
    borrowers = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'data': borrowers_schema.dump(borrowers),
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': (total + page_size - 1) // page_size,
    }), 200


@api_bp.route('/borrowers', methods=['POST'])
@jwt_required()
def create_borrower():
    """Create a new borrower."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        data = BorrowerCreateSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400

    # Check if DPI already exists
    if Borrower.query.filter_by(dpi=data['dpi']).first():
        return jsonify({'message': 'A borrower with this DPI already exists'}), 409

    # Create borrower
    borrower = Borrower(
        dpi=data['dpi'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data.get('email'),
        phone=data['phone'],
        alternate_phone=data.get('alternate_phone'),
        address=data['address'],
        municipality=data['municipality'],
        department=data['department'],
        occupation=data.get('occupation'),
        employer=data.get('employer'),
        monthly_income=data.get('monthly_income'),
        risk_tier=data.get('risk_tier', 'Medium'),
        verification_status='Pending',
        notes=data.get('notes'),
    )
    db.session.add(borrower)
    db.session.commit()

    return jsonify(borrower_schema.dump(borrower)), 201


@api_bp.route('/borrowers/<borrower_id>', methods=['GET'])
@jwt_required()
def get_borrower(borrower_id):
    """Get borrower details by ID."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    borrower = Borrower.query.get(borrower_id)
    if not borrower:
        return jsonify({'message': 'Borrower not found'}), 404

    return jsonify(borrower_schema.dump(borrower)), 200


@api_bp.route('/borrowers/<borrower_id>', methods=['PUT'])
@jwt_required()
def update_borrower(borrower_id):
    """Update borrower details."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    borrower = Borrower.query.get(borrower_id)
    if not borrower:
        return jsonify({'message': 'Borrower not found'}), 404

    data = request.get_json()

    # Update fields
    if 'firstName' in data:
        borrower.first_name = data['firstName']
    if 'lastName' in data:
        borrower.last_name = data['lastName']
    if 'email' in data:
        borrower.email = data['email']
    if 'phone' in data:
        borrower.phone = data['phone']
    if 'alternatePhone' in data:
        borrower.alternate_phone = data['alternatePhone']
    if 'address' in data:
        borrower.address = data['address']
    if 'municipality' in data:
        borrower.municipality = data['municipality']
    if 'department' in data:
        borrower.department = data['department']
    if 'occupation' in data:
        borrower.occupation = data['occupation']
    if 'employer' in data:
        borrower.employer = data['employer']
    if 'monthlyIncome' in data:
        borrower.monthly_income = data['monthlyIncome']
    if 'riskTier' in data:
        borrower.risk_tier = data['riskTier']
    if 'notes' in data:
        borrower.notes = data['notes']

    borrower.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(borrower_schema.dump(borrower)), 200


@api_bp.route('/borrowers/<borrower_id>/verify', methods=['POST'])
@jwt_required()
def verify_borrower(borrower_id):
    """Verify a borrower."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    borrower = Borrower.query.get(borrower_id)
    if not borrower:
        return jsonify({'message': 'Borrower not found'}), 404

    data = request.get_json() or {}
    status = data.get('status', 'Verified')

    if status not in ['Verified', 'Rejected']:
        return jsonify({'message': 'Invalid status'}), 400

    borrower.verification_status = status
    borrower.verified_by_id = user.id
    borrower.verified_at = datetime.utcnow()
    borrower.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(borrower_schema.dump(borrower)), 200


@api_bp.route('/borrowers/<borrower_id>/loans', methods=['GET'])
@jwt_required()
def get_borrower_loans(borrower_id):
    """Get all loans for a borrower."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    borrower = Borrower.query.get(borrower_id)
    if not borrower:
        return jsonify({'message': 'Borrower not found'}), 404

    loans = Loan.query.filter_by(borrower_id=borrower_id).order_by(
        Loan.created_at.desc()
    ).all()

    return jsonify({'data': loans_schema.dump(loans)}), 200
