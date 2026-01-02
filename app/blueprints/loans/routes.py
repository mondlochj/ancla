from datetime import date
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from . import loans_bp
from .forms import LoanForm, LoanApprovalForm, LoanActivationForm
from ...models.loan import Loan, LoanProduct, LoanStatus
from ...models.borrower import Borrower
from ...models.property import Property
from ...extensions import db
from ...utils.decorators import internal_only, role_required
from ...utils.helpers import calculate_ltv
from ...services.loan_service import (
    approve_loan, activate_loan, validate_loan_for_approval,
    validate_loan_for_activation, LoanValidationError, get_loan_summary
)
from ...services.audit_service import log_loan_action
from ...services.email import send_loan_notification


@loans_bp.route('/')
@login_required
@internal_only
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Loan.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    if search:
        query = query.join(Borrower).filter(
            db.or_(
                Loan.loan_number.ilike(f'%{search}%'),
                Borrower.full_name.ilike(f'%{search}%'),
                Borrower.dpi.ilike(f'%{search}%'),
                Borrower.email.ilike(f'%{search}%')
            )
        )

    loans = query.order_by(Loan.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('loans/index.html',
                          loans=loans,
                          status_filter=status_filter,
                          search=search,
                          LoanStatus=LoanStatus)


@loans_bp.route('/my-loans')
@login_required
def my_loans():
    """View for borrowers to see their own loans."""
    if not current_user.borrower_profile:
        flash('No borrower profile linked to your account.', 'warning')
        return render_template('loans/my_loans.html', loans=[])

    loans = current_user.borrower_profile.loans.order_by(Loan.created_at.desc()).all()
    return render_template('loans/my_loans.html', loans=loans)


@loans_bp.route('/my-loans/<uuid:id>')
@login_required
def borrower_loan_view(id):
    """Borrower view of their own loan with documents."""
    loan = Loan.query.get_or_404(id)

    # Verify this is the borrower's loan
    if not current_user.borrower_profile or \
       loan.borrower_id != current_user.borrower_profile.id:
        abort(403)

    summary = None
    if loan.status in ['Active', 'Matured', 'Defaulted', 'LegalReady']:
        summary = get_loan_summary(loan)

    return render_template('loans/borrower_view.html',
                          loan=loan,
                          summary=summary)


@loans_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'CreditOfficer')
def create():
    borrower_id = request.args.get('borrower_id')
    property_id = request.args.get('property_id')

    borrower = None
    property_obj = None

    if borrower_id:
        borrower = Borrower.query.get_or_404(borrower_id)
        if not borrower.is_verified:
            flash('Borrower must be verified before creating a loan.', 'danger')
            return redirect(url_for('borrowers.view', id=borrower_id))

    if property_id:
        property_obj = Property.query.get_or_404(property_id)
        if not property_obj.verified:
            flash('Property must be verified before creating a loan.', 'danger')
            return redirect(url_for('collateral.view', id=property_id))
        if property_obj.has_active_loan():
            flash('Property already has an active loan.', 'danger')
            return redirect(url_for('collateral.view', id=property_id))
        borrower = property_obj.borrower

    form = LoanForm()

    # Get properties for borrower selection
    available_properties = []
    if borrower:
        available_properties = [
            p for p in borrower.properties
            if p.verified and not p.has_active_loan()
        ]

    if form.validate_on_submit():
        if not borrower_id or not property_id:
            flash('Borrower and property are required.', 'danger')
            return redirect(url_for('loans.create'))

        property_obj = Property.query.get_or_404(property_id)

        # Calculate LTV
        ltv = calculate_ltv(form.loan_amount.data, property_obj.market_value)

        loan = Loan(
            loan_number=Loan.generate_loan_number(),
            borrower_id=borrower_id,
            property_id=property_id,
            product_id=form.product_id.data,
            loan_amount=form.loan_amount.data,
            interest_rate=form.interest_rate.data,
            term_months=form.term_months.data,
            ltv=ltv,
            status=LoanStatus.DRAFT.value,
            created_by=current_user.id
        )

        db.session.add(loan)
        db.session.commit()

        log_loan_action(loan, 'created')

        flash('Loan created successfully.', 'success')
        return redirect(url_for('loans.view', id=loan.id))

    # Pre-populate from product if selected
    if form.product_id.data:
        product = LoanProduct.query.get(form.product_id.data)
        if product and not form.interest_rate.data:
            form.interest_rate.data = product.interest_rate
            form.term_months.data = product.min_term_months

    return render_template('loans/form.html',
                          form=form,
                          borrower=borrower,
                          property=property_obj,
                          available_properties=available_properties,
                          title='New Loan Application')


@loans_bp.route('/<uuid:id>')
@login_required
def view(id):
    loan = Loan.query.get_or_404(id)

    # Borrowers can only view their own loans
    if current_user.role.name == 'Borrower':
        if not current_user.borrower_profile or loan.borrower_id != current_user.borrower_profile.id:
            abort(403)

    approval_form = LoanApprovalForm()
    activation_form = LoanActivationForm()
    validation_errors = []

    if loan.status == LoanStatus.UNDER_REVIEW.value:
        validation_errors = validate_loan_for_approval(loan)
    elif loan.status == LoanStatus.APPROVED.value:
        validation_errors = validate_loan_for_activation(loan)

    summary = get_loan_summary(loan)

    return render_template('loans/view.html',
                          loan=loan,
                          approval_form=approval_form,
                          activation_form=activation_form,
                          validation_errors=validation_errors,
                          summary=summary,
                          LoanStatus=LoanStatus)


@loans_bp.route('/<uuid:id>/submit', methods=['POST'])
@login_required
@role_required('Admin', 'CreditOfficer')
def submit_for_review(id):
    loan = Loan.query.get_or_404(id)

    if loan.status != LoanStatus.DRAFT.value:
        flash('Only draft loans can be submitted for review.', 'danger')
        return redirect(url_for('loans.view', id=loan.id))

    loan.status = LoanStatus.UNDER_REVIEW.value
    db.session.commit()

    log_loan_action(loan, 'submitted_for_review')

    flash('Loan submitted for review.', 'success')
    return redirect(url_for('loans.view', id=loan.id))


@loans_bp.route('/<uuid:id>/approve', methods=['POST'])
@login_required
@role_required('Admin', 'CreditOfficer')
def approve(id):
    loan = Loan.query.get_or_404(id)
    form = LoanApprovalForm()

    if form.validate_on_submit():
        if 'submit_approve' in request.form:
            try:
                approve_loan(loan, current_user, form.approval_notes.data)
                db.session.commit()
                log_loan_action(loan, 'approved')
                # Send email notification to borrower
                if loan.borrower.email:
                    send_loan_notification(loan.borrower, loan, 'approved')
                flash('Loan approved successfully.', 'success')
            except LoanValidationError as e:
                flash(f'Cannot approve loan: {str(e)}', 'danger')

        elif 'submit_reject' in request.form:
            loan.status = LoanStatus.DRAFT.value
            loan.approval_notes = form.approval_notes.data
            db.session.commit()
            log_loan_action(loan, 'returned_to_draft')
            flash('Loan returned to draft.', 'warning')

    return redirect(url_for('loans.view', id=loan.id))


@loans_bp.route('/<uuid:id>/activate', methods=['POST'])
@login_required
@role_required('Admin', 'CreditOfficer')
def activate(id):
    loan = Loan.query.get_or_404(id)
    form = LoanActivationForm()

    if form.validate_on_submit():
        try:
            activate_loan(loan, form.disbursement_notes.data)
            db.session.commit()
            log_loan_action(loan, 'activated', new_values={
                'disbursement_date': str(loan.disbursement_date),
                'maturity_date': str(loan.maturity_date)
            })
            # Send email notification to borrower
            if loan.borrower.email:
                send_loan_notification(loan.borrower, loan, 'activated')
            flash('Loan activated. Payment schedule generated.', 'success')
        except LoanValidationError as e:
            flash(f'Cannot activate loan: {str(e)}', 'danger')

    return redirect(url_for('loans.view', id=loan.id))


@loans_bp.route('/<uuid:id>/close', methods=['POST'])
@login_required
@role_required('Admin')
def close(id):
    loan = Loan.query.get_or_404(id)

    if loan.status not in [LoanStatus.MATURED.value, LoanStatus.DEFAULTED.value,
                           LoanStatus.LEGAL_READY.value]:
        flash('Cannot close loan in current status.', 'danger')
        return redirect(url_for('loans.view', id=loan.id))

    old_status = loan.status
    loan.status = LoanStatus.CLOSED.value
    db.session.commit()

    log_loan_action(loan, 'closed', old_values={'status': old_status})

    flash('Loan closed.', 'info')
    return redirect(url_for('loans.view', id=loan.id))
