from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import collections_bp
from .forms import CollectionActionForm, ExtensionForm, LegalEscalationForm
from ...models.collection import CollectionAction, CollectionStage, ActionType
from ...models.loan import Loan, LoanStatus
from ...models.payment import PaymentSchedule
from ...extensions import db
from ...utils.decorators import role_required
from ...services.audit_service import log_loan_action


@collections_bp.route('/')
@login_required
@role_required('Admin', 'Collections')
def index():
    """Collections dashboard showing delinquent loans."""
    today = date.today()

    # Get loans with overdue payments
    delinquent_loans = db.session.query(Loan).join(PaymentSchedule).filter(
        PaymentSchedule.is_paid == False,
        PaymentSchedule.due_date < today,
        Loan.status.in_([LoanStatus.ACTIVE.value, LoanStatus.MATURED.value,
                        LoanStatus.DEFAULTED.value, LoanStatus.LEGAL_READY.value])
    ).distinct().all()

    # Categorize by stage
    loans_by_stage = {
        'grace': [],
        'reminder': [],
        'delinquent': [],
        'legal_ready': []
    }

    for loan in delinquent_loans:
        days = loan.days_past_due
        stage = CollectionAction.determine_stage(days)

        if stage == CollectionStage.GRACE.value:
            loans_by_stage['grace'].append((loan, days))
        elif stage == CollectionStage.REMINDER.value:
            loans_by_stage['reminder'].append((loan, days))
        elif stage == CollectionStage.DELINQUENT.value:
            loans_by_stage['delinquent'].append((loan, days))
        else:
            loans_by_stage['legal_ready'].append((loan, days))

    return render_template('collections/index.html',
                          loans_by_stage=loans_by_stage,
                          today=today)


@collections_bp.route('/loan/<uuid:loan_id>')
@login_required
@role_required('Admin', 'Collections')
def loan_detail(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    actions = loan.collection_actions.order_by(CollectionAction.created_at.desc()).all()
    action_form = CollectionActionForm()
    extension_form = ExtensionForm()
    legal_form = LegalEscalationForm()

    current_stage = CollectionAction.determine_stage(loan.days_past_due)

    return render_template('collections/loan_detail.html',
                          loan=loan,
                          actions=actions,
                          action_form=action_form,
                          extension_form=extension_form,
                          legal_form=legal_form,
                          current_stage=current_stage)


@collections_bp.route('/loan/<uuid:loan_id>/action', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Collections')
def create_action(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    form = CollectionActionForm()

    if form.validate_on_submit():
        current_stage = CollectionAction.determine_stage(loan.days_past_due)

        action = CollectionAction(
            loan_id=loan.id,
            stage=current_stage,
            action_type=form.action_type.data,
            notes=form.notes.data,
            contact_name=form.contact_name.data,
            contact_phone=form.contact_phone.data,
            contact_result=form.contact_result.data,
            promise_amount=form.promise_amount.data,
            promise_date=form.promise_date.data,
            created_by=current_user.id
        )

        db.session.add(action)
        db.session.commit()

        flash('Collection action recorded.', 'success')
        return redirect(url_for('collections.loan_detail', loan_id=loan.id))

    return render_template('collections/action_form.html', form=form, loan=loan)


@collections_bp.route('/loan/<uuid:loan_id>/extension', methods=['POST'])
@login_required
@role_required('Admin', 'Collections')
def grant_extension(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    form = ExtensionForm()

    if form.validate_on_submit():
        # Find next unpaid schedule item and extend
        next_due = loan.schedule.filter_by(is_paid=False).first()
        if next_due:
            new_due_date = next_due.due_date + relativedelta(days=form.extension_days.data)

            action = CollectionAction(
                loan_id=loan.id,
                stage=CollectionAction.determine_stage(loan.days_past_due),
                action_type=ActionType.EXTENSION_GRANTED.value,
                notes=form.notes.data,
                extension_granted=True,
                extension_days=form.extension_days.data,
                new_due_date=new_due_date,
                created_by=current_user.id
            )

            # Update the schedule item
            next_due.due_date = new_due_date
            next_due.late_fee = 0  # Reset late fee on extension

            db.session.add(action)
            db.session.commit()

            log_loan_action(loan, 'extension_granted', new_values={
                'extension_days': form.extension_days.data,
                'new_due_date': str(new_due_date)
            })

            flash(f'Extension of {form.extension_days.data} days granted.', 'success')
        else:
            flash('No pending payments to extend.', 'warning')

    return redirect(url_for('collections.loan_detail', loan_id=loan.id))


@collections_bp.route('/loan/<uuid:loan_id>/escalate', methods=['POST'])
@login_required
@role_required('Admin')
def escalate_to_legal(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    form = LegalEscalationForm()

    if form.validate_on_submit():
        if loan.status not in [LoanStatus.DEFAULTED.value]:
            flash('Only defaulted loans can be escalated to legal.', 'warning')
            return redirect(url_for('collections.loan_detail', loan_id=loan.id))

        action = CollectionAction(
            loan_id=loan.id,
            stage=CollectionStage.LEGAL_READY.value,
            action_type=ActionType.LEGAL_NOTICE.value,
            notes=form.notes.data,
            escalated_to_legal=True,
            escalation_date=datetime.utcnow(),
            created_by=current_user.id
        )

        loan.status = LoanStatus.LEGAL_READY.value

        db.session.add(action)
        db.session.commit()

        log_loan_action(loan, 'escalated_to_legal')

        flash('Loan escalated to legal status.', 'warning')

    return redirect(url_for('collections.loan_detail', loan_id=loan.id))
