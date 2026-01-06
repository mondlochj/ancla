"""
Dashboard API endpoints.

Provides portfolio metrics and analytics for the dashboard.
"""

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta

from . import api_bp
from app.extensions import db
from app.models import Loan, Payment, PaymentSchedule, User, Borrower, Property
from app.models.loan import LoanStatus
from app.schemas import LoanSchema


loan_schema = LoanSchema(many=True)


@api_bp.route('/dashboard/metrics', methods=['GET'])
@jwt_required()
def get_dashboard_metrics():
    """Get dashboard metrics including portfolio value, loan counts, and default rates."""
    # Get user for role check
    user = User.query.get(get_jwt_identity())
    if not user or user.role.name == 'Borrower':
        return jsonify({'message': 'Unauthorized'}), 403

    # Portfolio value (sum of active loan amounts)
    total_portfolio = db.session.query(func.sum(Loan.amount)).filter(
        Loan.status == LoanStatus.ACTIVE
    ).scalar() or 0

    # Active loans count
    active_loans_count = Loan.query.filter(Loan.status == LoanStatus.ACTIVE).count()

    # Default rate
    defaulted_count = Loan.query.filter(
        Loan.status.in_([LoanStatus.DEFAULTED, LoanStatus.LEGAL_READY])
    ).count()
    total_completed = Loan.query.filter(
        Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.MATURED, LoanStatus.DEFAULTED, LoanStatus.LEGAL_READY, LoanStatus.CLOSED])
    ).count()
    default_rate = defaulted_count / total_completed if total_completed > 0 else 0

    # Average LTV
    avg_ltv = db.session.query(func.avg(Loan.ltv)).filter(
        Loan.status == LoanStatus.ACTIVE
    ).scalar() or 0

    # Monthly interest income (estimated from active loans)
    monthly_interest = db.session.query(
        func.sum(Loan.amount * Loan.interest_rate)
    ).filter(Loan.status == LoanStatus.ACTIVE).scalar() or 0

    # Overdue payments
    today = datetime.utcnow().date()
    overdue_schedules = PaymentSchedule.query.filter(
        PaymentSchedule.due_date < today,
        PaymentSchedule.status.in_(['Pending', 'Partial'])
    ).all()
    overdue_count = len(overdue_schedules)
    overdue_amount = sum(s.total_due - s.principal_paid - s.interest_paid - s.late_fee_paid for s in overdue_schedules)

    # Loans by status
    loans_by_status = {}
    for status in LoanStatus:
        count = Loan.query.filter(Loan.status == status).count()
        loans_by_status[status.value] = count

    # Loans by department (through borrower -> property)
    loans_by_dept = db.session.query(
        Property.department,
        func.count(Loan.id)
    ).join(Loan, Loan.property_id == Property.id).filter(
        Loan.status == LoanStatus.ACTIVE
    ).group_by(Property.department).all()
    loans_by_department = {dept: count for dept, count in loans_by_dept if dept}

    # Recent loans
    recent_loans = Loan.query.order_by(Loan.created_at.desc()).limit(5).all()

    return jsonify({
        'totalPortfolioValue': float(total_portfolio),
        'activeLoansCount': active_loans_count,
        'defaultRate': float(default_rate),
        'averageLtv': float(avg_ltv),
        'monthlyInterestIncome': float(monthly_interest),
        'overduePaymentsCount': overdue_count,
        'overdueAmount': float(overdue_amount),
        'loansByStatus': loans_by_status,
        'loansByDepartment': loans_by_department,
        'recentLoans': loan_schema.dump(recent_loans),
    }), 200


@api_bp.route('/dashboard/portfolio', methods=['GET'])
@jwt_required()
def get_portfolio_summary():
    """Get detailed portfolio summary with trends."""
    user = User.query.get(get_jwt_identity())
    if not user or user.role.name == 'Borrower':
        return jsonify({'message': 'Unauthorized'}), 403

    # Get trends for last 6 months
    months = []
    today = datetime.utcnow()
    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        months.append(month_start)

    # Portfolio value trend
    portfolio_trend = []
    for month in months:
        next_month = (month + timedelta(days=32)).replace(day=1)
        value = db.session.query(func.sum(Loan.amount)).filter(
            Loan.activated_at < next_month,
            Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.MATURED])
        ).scalar() or 0
        portfolio_trend.append({
            'month': month.strftime('%Y-%m'),
            'value': float(value)
        })

    return jsonify({
        'portfolioTrend': portfolio_trend,
    }), 200
