from datetime import date
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import payments_bp
from .forms import PaymentForm
from ...models.payment import Payment, PaymentSchedule
from ...models.loan import Loan, LoanStatus
from ...extensions import db
from ...utils.decorators import internal_only, role_required
from ...services.payment_service import record_payment, get_loan_payment_summary
from ...services.audit_service import log_payment_action
from ...services.email import send_loan_notification


@payments_bp.route('/')
@login_required
@internal_only
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Payment.query

    if search:
        from ...models.borrower import Borrower
        query = query.join(Loan).join(Borrower).filter(
            db.or_(
                Loan.loan_number.ilike(f'%{search}%'),
                Borrower.full_name.ilike(f'%{search}%'),
                Borrower.dpi.ilike(f'%{search}%'),
                Borrower.email.ilike(f'%{search}%')
            )
        )

    payments = query.order_by(Payment.payment_date.desc()).paginate(
        page=page, per_page=30, error_out=False
    )

    return render_template('payments/index.html',
                          payments=payments,
                          search=search)


@payments_bp.route('/record', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'CreditOfficer', 'Collections')
def record():
    loan_id = request.args.get('loan_id')
    loan = None
    if loan_id:
        loan = Loan.query.get_or_404(loan_id)
        if loan.status not in [LoanStatus.ACTIVE.value, LoanStatus.MATURED.value,
                               LoanStatus.DEFAULTED.value]:
            flash('Cannot record payments for loans not in active status.', 'warning')
            return redirect(url_for('loans.view', id=loan_id))

    form = PaymentForm()
    if not form.payment_date.data:
        form.payment_date.data = date.today()

    if form.validate_on_submit():
        if not loan_id:
            flash('Loan is required.', 'danger')
            return redirect(url_for('payments.record'))

        payment = record_payment(
            loan=loan,
            amount=form.amount.data,
            payment_type=form.payment_type.data,
            payment_date=form.payment_date.data,
            recorded_by=current_user.id,
            payment_method=form.payment_method.data,
            reference_number=form.reference_number.data,
            notes=form.notes.data
        )
        db.session.commit()

        log_payment_action(payment, 'recorded', new_values={
            'amount': str(payment.amount),
            'type': payment.payment_type
        })

        # Send email notification to borrower
        if loan.borrower.email:
            send_loan_notification(
                loan.borrower, loan, 'payment_received',
                extra_info={'payment_amount': payment.amount}
            )

        flash(f'Payment of Q{payment.amount:,.2f} recorded successfully.', 'success')
        return redirect(url_for('loans.view', id=loan_id))

    # Pre-fill with next due amount if available
    if loan:
        next_due = loan.schedule.filter_by(is_paid=False).first()
        if next_due and not form.amount.data:
            form.amount.data = next_due.total_due

    return render_template('payments/record.html', form=form, loan=loan)


@payments_bp.route('/loan/<uuid:loan_id>')
@login_required
@internal_only
def loan_payments(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    payments = loan.payments.order_by(Payment.payment_date.desc()).all()
    summary = get_loan_payment_summary(loan)

    return render_template('payments/loan_payments.html',
                          loan=loan,
                          payments=payments,
                          summary=summary)


@payments_bp.route('/overdue')
@login_required
@role_required('Admin', 'Collections')
def overdue():
    """View overdue payments."""
    today = date.today()

    overdue_items = db.session.query(
        PaymentSchedule, Loan
    ).join(Loan).filter(
        PaymentSchedule.is_paid == False,
        PaymentSchedule.due_date < today,
        Loan.status.in_([LoanStatus.ACTIVE.value, LoanStatus.MATURED.value, LoanStatus.DEFAULTED.value])
    ).order_by(PaymentSchedule.due_date).all()

    return render_template('payments/overdue.html', overdue_items=overdue_items, today=today)
