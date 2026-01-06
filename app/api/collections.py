"""
Collections API endpoints.

Provides endpoints for collections workflow.
"""

from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from . import api_bp
from app.extensions import db
from app.models import Loan, CollectionAction, PaymentSchedule, User
from app.models.loan import LoanStatus
from app.schemas import LoanSchema, CollectionActionSchema, CollectionActionCreateSchema


loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)
action_schema = CollectionActionSchema()
actions_schema = CollectionActionSchema(many=True)


def check_collections_user():
    """Check if current user can access collections."""
    user = User.query.get(get_jwt_identity())
    if not user or user.role.name not in ['Admin', 'Collections']:
        return None
    return user


@api_bp.route('/collections/delinquent', methods=['GET'])
@jwt_required()
def get_delinquent_loans():
    """Get list of delinquent loans for collections."""
    user = check_collections_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)

    today = datetime.utcnow().date()

    # Get loans with overdue payments
    from sqlalchemy import func, distinct

    overdue_loan_ids = db.session.query(distinct(PaymentSchedule.loan_id)).filter(
        PaymentSchedule.due_date < today,
        PaymentSchedule.status.in_(['Pending', 'Partial'])
    ).subquery()

    query = Loan.query.filter(
        Loan.id.in_(overdue_loan_ids),
        Loan.status == LoanStatus.ACTIVE
    )

    # Paginate
    total = query.count()
    loans = query.offset((page - 1) * page_size).limit(page_size).all()

    # Add days overdue to each loan
    result = []
    for loan in loans:
        loan_data = loan_schema.dump(loan)
        oldest_overdue = PaymentSchedule.query.filter(
            PaymentSchedule.loan_id == loan.id,
            PaymentSchedule.due_date < today,
            PaymentSchedule.status.in_(['Pending', 'Partial'])
        ).order_by(PaymentSchedule.due_date).first()

        if oldest_overdue:
            loan_data['daysOverdue'] = (today - oldest_overdue.due_date).days
            loan_data['overdueAmount'] = (
                oldest_overdue.total_due -
                oldest_overdue.principal_paid -
                oldest_overdue.interest_paid -
                oldest_overdue.late_fee_paid
            )
        result.append(loan_data)

    return jsonify({
        'data': result,
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': (total + page_size - 1) // page_size,
    }), 200


@api_bp.route('/collections/<loan_id>', methods=['GET'])
@jwt_required()
def get_loan_collection_details(loan_id):
    """Get collection details for a loan."""
    user = check_collections_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    today = datetime.utcnow().date()

    # Get overdue schedules
    overdue_schedules = PaymentSchedule.query.filter(
        PaymentSchedule.loan_id == loan_id,
        PaymentSchedule.due_date < today,
        PaymentSchedule.status.in_(['Pending', 'Partial'])
    ).order_by(PaymentSchedule.due_date).all()

    # Get collection actions
    actions = CollectionAction.query.filter_by(loan_id=loan_id).order_by(
        CollectionAction.created_at.desc()
    ).all()

    # Calculate totals
    total_overdue = sum(
        s.total_due - s.principal_paid - s.interest_paid - s.late_fee_paid
        for s in overdue_schedules
    )
    days_overdue = (today - overdue_schedules[0].due_date).days if overdue_schedules else 0

    from app.schemas import PaymentScheduleSchema
    schedule_schema = PaymentScheduleSchema(many=True)

    return jsonify({
        'loan': loan_schema.dump(loan),
        'overdueSchedules': schedule_schema.dump(overdue_schedules),
        'actions': actions_schema.dump(actions),
        'totalOverdue': float(total_overdue),
        'daysOverdue': days_overdue,
    }), 200


@api_bp.route('/collections/<loan_id>/actions', methods=['GET'])
@jwt_required()
def get_collection_actions(loan_id):
    """Get collection action history for a loan."""
    user = check_collections_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    actions = CollectionAction.query.filter_by(loan_id=loan_id).order_by(
        CollectionAction.created_at.desc()
    ).all()

    return jsonify({
        'data': actions_schema.dump(actions),
        'total': len(actions),
    }), 200


@api_bp.route('/collections/<loan_id>/action', methods=['POST'])
@jwt_required()
def create_collection_action(loan_id):
    """Record a collection action."""
    user = check_collections_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    try:
        data = CollectionActionCreateSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400

    # Create action
    action = CollectionAction(
        loan_id=loan_id,
        action_type=data['action_type'],
        contacted_person=data.get('contacted_person'),
        contact_phone=data.get('contact_phone'),
        outcome=data.get('outcome'),
        promise_amount=data.get('promise_amount'),
        promise_date=data.get('promise_date'),
        extension_date=data.get('extension_date'),
        performed_by_id=user.id,
        notes=data.get('notes'),
    )
    db.session.add(action)
    db.session.commit()

    return jsonify(action_schema.dump(action)), 201
