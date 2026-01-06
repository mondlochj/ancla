"""
Payments API endpoints.

Provides CRUD operations for payments.
"""

from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from . import api_bp
from app.extensions import db
from app.models import Payment, PaymentSchedule, Loan, User
from app.schemas import PaymentSchema, PaymentCreateSchema, PaymentScheduleSchema
from app.services.payment_service import allocate_payment


payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)
schedule_schema = PaymentScheduleSchema(many=True)


def check_internal_user():
    """Check if current user is an internal user (not borrower)."""
    user = User.query.get(get_jwt_identity())
    if not user or user.role.name == 'Borrower':
        return None
    return user


@api_bp.route('/payments', methods=['GET'])
@jwt_required()
def get_payments():
    """Get paginated list of payments with optional filters."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    loan_id = request.args.get('loanId')
    payment_type = request.args.get('paymentType')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    # Build query
    query = Payment.query

    if loan_id:
        query = query.filter(Payment.loan_id == loan_id)

    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)

    if start_date:
        query = query.filter(Payment.created_at >= start_date)

    if end_date:
        query = query.filter(Payment.created_at <= end_date)

    # Order by date
    query = query.order_by(Payment.created_at.desc())

    # Paginate
    total = query.count()
    payments = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'data': payments_schema.dump(payments),
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': (total + page_size - 1) // page_size,
    }), 200


@api_bp.route('/payments', methods=['POST'])
@jwt_required()
def create_payment():
    """Record a new payment."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer', 'Collections']:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        data = PaymentCreateSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400

    # Validate loan exists
    loan = Loan.query.get(data['loan_id'])
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    # Create payment
    payment = Payment(
        loan_id=data['loan_id'],
        schedule_id=data.get('schedule_id'),
        amount=data['amount'],
        payment_type=data['payment_type'],
        payment_method=data['payment_method'],
        reference_number=data.get('reference_number'),
        received_by_id=user.id,
        notes=data.get('notes'),
    )
    db.session.add(payment)

    # Allocate payment to schedule if applicable
    if data.get('schedule_id'):
        schedule = PaymentSchedule.query.get(data['schedule_id'])
        if schedule:
            allocate_payment(payment, schedule)

    db.session.commit()

    return jsonify(payment_schema.dump(payment)), 201


@api_bp.route('/payments/<payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get payment details by ID."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'message': 'Payment not found'}), 404

    return jsonify(payment_schema.dump(payment)), 200


@api_bp.route('/payments/overdue', methods=['GET'])
@jwt_required()
def get_overdue_payments():
    """Get list of overdue payments."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    today = datetime.utcnow().date()

    overdue_schedules = PaymentSchedule.query.filter(
        PaymentSchedule.due_date < today,
        PaymentSchedule.status.in_(['Pending', 'Partial'])
    ).order_by(PaymentSchedule.due_date).all()

    return jsonify({
        'data': schedule_schema.dump(overdue_schedules),
        'total': len(overdue_schedules),
    }), 200


@api_bp.route('/loans/<loan_id>/schedule', methods=['GET'])
@jwt_required()
def get_payment_schedule(loan_id):
    """Get payment schedule for a loan."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    # Check authorization
    if user.role.name == 'Borrower':
        from app.models import Borrower
        borrower = Borrower.query.filter_by(user_id=user_id).first()
        if not borrower or str(loan.borrower_id) != str(borrower.id):
            return jsonify({'message': 'Unauthorized'}), 403

    schedules = PaymentSchedule.query.filter_by(loan_id=loan_id).order_by(
        PaymentSchedule.due_date
    ).all()

    return jsonify({'data': schedule_schema.dump(schedules)}), 200
