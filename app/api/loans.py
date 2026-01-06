"""
Loans API endpoints.

Provides CRUD operations for loans.
"""

from datetime import datetime, timedelta
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_

from . import api_bp
from app.extensions import db
from app.models import Loan, LoanProduct, Borrower, Property, User, PaymentSchedule
from app.models.loan import LoanStatus
from app.schemas import LoanSchema, LoanCreateSchema, PaymentScheduleSchema
from app.services.loan_service import generate_reference_number, generate_payment_schedule


loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)
schedule_schema = PaymentScheduleSchema(many=True)


def check_internal_user():
    """Check if current user is an internal user (not borrower)."""
    user = User.query.get(get_jwt_identity())
    if not user or user.role.name == 'Borrower':
        return None
    return user


@api_bp.route('/loans', methods=['GET'])
@jwt_required()
def get_loans():
    """Get paginated list of loans with optional filters."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    status = request.args.get('status')
    borrower_id = request.args.get('borrowerId')
    search = request.args.get('search', '')

    # Build query
    query = Loan.query

    if status:
        try:
            query = query.filter(Loan.status == LoanStatus(status))
        except ValueError:
            pass

    if borrower_id:
        query = query.filter(Loan.borrower_id == borrower_id)

    if search:
        query = query.join(Borrower).filter(
            or_(
                Loan.reference_number.ilike(f'%{search}%'),
                Borrower.first_name.ilike(f'%{search}%'),
                Borrower.last_name.ilike(f'%{search}%'),
            )
        )

    # Order by created date
    query = query.order_by(Loan.created_at.desc())

    # Paginate
    total = query.count()
    loans = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'data': loans_schema.dump(loans),
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': (total + page_size - 1) // page_size,
    }), 200


@api_bp.route('/loans', methods=['POST'])
@jwt_required()
def create_loan():
    """Create a new loan."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        data = LoanCreateSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400

    # Validate borrower exists
    borrower = Borrower.query.get(data['borrower_id'])
    if not borrower:
        return jsonify({'message': 'Borrower not found'}), 404

    # Validate property exists
    property = Property.query.get(data['property_id'])
    if not property:
        return jsonify({'message': 'Property not found'}), 404

    # Validate loan product exists
    loan_product = LoanProduct.query.get(data['loan_product_id'])
    if not loan_product:
        return jsonify({'message': 'Loan product not found'}), 404

    # Calculate LTV
    ltv = data['amount'] / property.market_value if property.market_value > 0 else 0
    if ltv > 0.40:
        return jsonify({'message': 'LTV cannot exceed 40%'}), 400

    # Create loan
    loan = Loan(
        reference_number=generate_reference_number(),
        borrower_id=data['borrower_id'],
        property_id=data['property_id'],
        loan_product_id=data['loan_product_id'],
        amount=data['amount'],
        term_months=data['term_months'],
        interest_rate=data['interest_rate'],
        ltv=ltv,
        status=LoanStatus.DRAFT,
        created_by_id=user.id,
        notes=data.get('notes'),
    )
    db.session.add(loan)
    db.session.commit()

    return jsonify(loan_schema.dump(loan)), 201


@api_bp.route('/loans/<loan_id>', methods=['GET'])
@jwt_required()
def get_loan(loan_id):
    """Get loan details by ID."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    # Borrowers can only view their own loans
    if user.role.name == 'Borrower':
        if str(loan.borrower.user_id) != str(user_id):
            return jsonify({'message': 'Unauthorized'}), 403

    return jsonify(loan_schema.dump(loan)), 200


@api_bp.route('/loans/<loan_id>', methods=['PUT'])
@jwt_required()
def update_loan(loan_id):
    """Update loan details."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    if loan.status not in [LoanStatus.DRAFT, LoanStatus.UNDER_REVIEW]:
        return jsonify({'message': 'Cannot modify loan in current status'}), 400

    data = request.get_json()

    # Update allowed fields
    if 'amount' in data:
        loan.amount = data['amount']
        if loan.property:
            loan.ltv = loan.amount / loan.property.market_value
    if 'termMonths' in data:
        loan.term_months = data['termMonths']
    if 'interestRate' in data:
        loan.interest_rate = data['interestRate']
    if 'notes' in data:
        loan.notes = data['notes']

    loan.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(loan_schema.dump(loan)), 200


@api_bp.route('/loans/<loan_id>/submit', methods=['POST'])
@jwt_required()
def submit_loan(loan_id):
    """Submit loan for review."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    if loan.status != LoanStatus.DRAFT:
        return jsonify({'message': 'Loan must be in draft status'}), 400

    loan.status = LoanStatus.UNDER_REVIEW
    loan.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(loan_schema.dump(loan)), 200


@api_bp.route('/loans/<loan_id>/approve', methods=['POST'])
@jwt_required()
def approve_loan(loan_id):
    """Approve a loan that is under review."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    if loan.status != LoanStatus.UNDER_REVIEW:
        return jsonify({'message': 'Loan must be under review to approve'}), 400

    data = request.get_json() or {}

    loan.status = LoanStatus.APPROVED
    loan.approved_by_id = user.id
    loan.approved_at = datetime.utcnow()
    loan.notes = data.get('notes', loan.notes)
    loan.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(loan_schema.dump(loan)), 200


@api_bp.route('/loans/<loan_id>/activate', methods=['POST'])
@jwt_required()
def activate_loan(loan_id):
    """Activate/disburse an approved loan."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    if loan.status != LoanStatus.APPROVED:
        return jsonify({'message': 'Loan must be approved to activate'}), 400

    # Activate loan
    loan.status = LoanStatus.ACTIVE
    loan.activated_at = datetime.utcnow()
    loan.maturity_date = (datetime.utcnow() + timedelta(days=30 * loan.term_months)).date()
    loan.updated_at = datetime.utcnow()

    # Generate payment schedule
    generate_payment_schedule(loan)

    db.session.commit()

    return jsonify(loan_schema.dump(loan)), 200


@api_bp.route('/loans/<loan_id>/schedule', methods=['GET'])
@jwt_required()
def get_loan_schedule(loan_id):
    """Get payment schedule for a loan."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    # Borrowers can only view their own loan schedule
    if user.role.name == 'Borrower':
        if str(loan.borrower.user_id) != str(user_id):
            return jsonify({'message': 'Unauthorized'}), 403

    schedules = PaymentSchedule.query.filter_by(loan_id=loan_id).order_by(
        PaymentSchedule.due_date
    ).all()

    return jsonify({'data': schedule_schema.dump(schedules)}), 200


@api_bp.route('/loans/<loan_id>/payments', methods=['GET'])
@jwt_required()
def get_loan_payments(loan_id):
    """Get payment history for a loan."""
    from app.models import Payment
    from app.schemas import PaymentSchema

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    # Borrowers can only view their own loan payments
    if user.role.name == 'Borrower':
        if str(loan.borrower.user_id) != str(user_id):
            return jsonify({'message': 'Unauthorized'}), 403

    payments = Payment.query.filter_by(loan_id=loan_id).order_by(
        Payment.created_at.desc()
    ).all()

    payment_schema = PaymentSchema(many=True)
    return jsonify({'data': payment_schema.dump(payments)}), 200


# Borrower portal endpoints
@api_bp.route('/my-loans', methods=['GET'])
@jwt_required()
def get_my_loans():
    """Get loans for the current borrower user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Find borrower linked to this user
    borrower = Borrower.query.filter_by(user_id=user_id).first()
    if not borrower:
        return jsonify({'data': [], 'total': 0}), 200

    loans = Loan.query.filter_by(borrower_id=borrower.id).order_by(
        Loan.created_at.desc()
    ).all()

    return jsonify({
        'data': loans_schema.dump(loans),
        'total': len(loans),
    }), 200
