from datetime import date, timedelta
from decimal import Decimal
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from . import admin_bp
from ...models.user import User, Role, RoleName
from ...models.borrower import Borrower
from ...models.property import Property
from ...models.loan import Loan, LoanStatus
from ...models.payment import Payment, PaymentSchedule
from ...models.audit import AuditLog
from ...extensions import db
from ...utils.decorators import admin_required, internal_only


@admin_bp.route('/')
@login_required
@internal_only
def dashboard():
    """Main dashboard with KPIs."""
    today = date.today()

    # Loan statistics
    total_active_loans = Loan.query.filter_by(status=LoanStatus.ACTIVE.value).count()
    total_portfolio = db.session.query(
        func.coalesce(func.sum(Loan.loan_amount), 0)
    ).filter(Loan.status == LoanStatus.ACTIVE.value).scalar()

    # Default rate
    defaulted_loans = Loan.query.filter(
        Loan.status.in_([LoanStatus.DEFAULTED.value, LoanStatus.LEGAL_READY.value])
    ).count()
    total_loans_ever = Loan.query.filter(
        Loan.status.notin_([LoanStatus.DRAFT.value])
    ).count()
    default_rate = (defaulted_loans / total_loans_ever * 100) if total_loans_ever > 0 else 0

    # Average LTV
    avg_ltv = db.session.query(
        func.avg(Loan.ltv)
    ).filter(Loan.status == LoanStatus.ACTIVE.value).scalar() or 0

    # Overdue amount
    overdue_schedules = db.session.query(
        func.coalesce(func.sum(PaymentSchedule.interest_due + PaymentSchedule.principal_due), 0)
    ).filter(
        PaymentSchedule.is_paid == False,
        PaymentSchedule.due_date < today
    ).scalar()

    # Interest income this month
    first_of_month = today.replace(day=1)
    monthly_interest = db.session.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.payment_type == 'Interest',
        Payment.payment_date >= first_of_month
    ).scalar()

    # Pending approvals
    pending_approvals = Loan.query.filter_by(status=LoanStatus.UNDER_REVIEW.value).count()

    # Loans by status
    loans_by_status = db.session.query(
        Loan.status, func.count(Loan.id)
    ).group_by(Loan.status).all()

    # Recent loans
    recent_loans = Loan.query.order_by(Loan.created_at.desc()).limit(5).all()

    # Loans by department (for regional analysis)
    loans_by_region = db.session.query(
        Property.department, func.count(Loan.id), func.sum(Loan.loan_amount)
    ).join(Loan).filter(
        Loan.status == LoanStatus.ACTIVE.value
    ).group_by(Property.department).all()

    return render_template('admin/dashboard.html',
                          total_active_loans=total_active_loans,
                          total_portfolio=total_portfolio,
                          default_rate=default_rate,
                          avg_ltv=avg_ltv,
                          overdue_amount=overdue_schedules,
                          monthly_interest=monthly_interest,
                          pending_approvals=pending_approvals,
                          loans_by_status=loans_by_status,
                          recent_loans=recent_loans,
                          loans_by_region=loans_by_region)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management."""
    users = User.query.order_by(User.created_at.desc()).all()
    roles = Role.query.all()
    return render_template('admin/users.html', users=users, roles=roles)


@admin_bp.route('/users/<uuid:id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(id):
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_active = not user.is_active
    db.session.commit()

    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.email} has been {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<uuid:id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(id):
    user = User.query.get_or_404(id)
    new_role_id = request.form.get('role_id', type=int)

    if not new_role_id:
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin.users'))

    if user.id == current_user.id:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('admin.users'))

    role = Role.query.get(new_role_id)
    if role:
        user.role_id = role.id
        db.session.commit()
        flash(f'User role changed to {role.name}.', 'success')

    return redirect(url_for('admin.users'))


@admin_bp.route('/audit-log')
@login_required
@admin_required
def audit_log():
    """View audit logs."""
    page = request.args.get('page', 1, type=int)
    entity_type = request.args.get('entity_type', '')
    action = request.args.get('action', '')

    query = AuditLog.query

    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    if action:
        query = query.filter_by(action=action)

    logs = query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    return render_template('admin/audit_log.html',
                          logs=logs,
                          entity_type=entity_type,
                          action=action)


@admin_bp.route('/reports')
@login_required
@internal_only
def reports():
    """Reports page."""
    return render_template('admin/reports.html')
