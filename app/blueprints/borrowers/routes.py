from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import borrowers_bp
from .forms import BorrowerForm, BorrowerVerificationForm, LinkUserForm
from ...models.borrower import Borrower, VerificationStatus
from ...models.user import User
from ...extensions import db
from ...utils.decorators import internal_only, role_required
from ...services.audit_service import log_borrower_action
from ...services.email import send_registration_invite


@borrowers_bp.route('/')
@login_required
@internal_only
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Borrower.query.filter_by(is_deleted=False)

    if status_filter:
        query = query.filter_by(verification_status=status_filter)

    if search:
        query = query.filter(
            db.or_(
                Borrower.full_name.ilike(f'%{search}%'),
                Borrower.dpi.ilike(f'%{search}%'),
                Borrower.phone.ilike(f'%{search}%'),
                Borrower.email.ilike(f'%{search}%')
            )
        )

    borrowers = query.order_by(Borrower.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('borrowers/index.html',
                          borrowers=borrowers,
                          status_filter=status_filter,
                          search=search)


@borrowers_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'CreditOfficer')
def create():
    form = BorrowerForm()

    if form.validate_on_submit():
        borrower = Borrower(
            full_name=form.full_name.data,
            dpi=form.dpi.data,
            nit=form.nit.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            department=form.department.data,
            municipality=form.municipality.data,
            employment_type=form.employment_type.data,
            employer_name=form.employer_name.data,
            business_name=form.business_name.data,
            monthly_income=form.monthly_income.data,
            risk_tier=form.risk_tier.data
        )

        # Check if user with this email already exists
        if form.email.data:
            existing_user = User.query.filter(User.email.ilike(form.email.data)).first()
            if existing_user:
                if existing_user.borrower_profile:
                    flash('A user with this email is already linked to another borrower.', 'warning')
                else:
                    borrower.user_id = existing_user.id
                    flash(f'Borrower automatically linked to existing user account ({existing_user.email}).', 'info')

        db.session.add(borrower)
        db.session.commit()

        log_borrower_action(borrower, 'created')

        # Send registration invite if no user was linked
        if form.email.data and not borrower.user_id:
            if send_registration_invite(form.email.data, form.full_name.data):
                flash('Registration invitation email sent to borrower.', 'info')
            else:
                flash('Could not send invitation email. Please check email configuration.', 'warning')

        flash('Borrower created successfully.', 'success')
        return redirect(url_for('borrowers.view', id=borrower.id))

    return render_template('borrowers/form.html', form=form, title='New Borrower')


@borrowers_bp.route('/<uuid:id>')
@login_required
@internal_only
def view(id):
    borrower = Borrower.query.get_or_404(id)
    verification_form = BorrowerVerificationForm()
    link_user_form = LinkUserForm()
    return render_template('borrowers/view.html',
                          borrower=borrower,
                          verification_form=verification_form,
                          link_user_form=link_user_form)


@borrowers_bp.route('/<uuid:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'CreditOfficer')
def edit(id):
    borrower = Borrower.query.get_or_404(id)
    form = BorrowerForm(obj=borrower)

    if form.validate_on_submit():
        old_values = {
            'full_name': borrower.full_name,
            'phone': borrower.phone,
            'risk_tier': borrower.risk_tier
        }

        form.populate_obj(borrower)
        db.session.commit()

        log_borrower_action(borrower, 'updated', old_values=old_values)

        flash('Borrower updated successfully.', 'success')
        return redirect(url_for('borrowers.view', id=borrower.id))

    return render_template('borrowers/form.html', form=form, borrower=borrower,
                          title='Edit Borrower')


@borrowers_bp.route('/<uuid:id>/verify', methods=['POST'])
@login_required
@role_required('Admin', 'CreditOfficer', 'Legal')
def verify(id):
    borrower = Borrower.query.get_or_404(id)
    form = BorrowerVerificationForm()

    if form.validate_on_submit():
        if 'submit_verify' in request.form:
            borrower.verify(current_user, form.verification_notes.data)
            log_borrower_action(borrower, 'verified')
            flash('Borrower verified successfully.', 'success')
        elif 'submit_reject' in request.form:
            borrower.reject(current_user, form.verification_notes.data)
            log_borrower_action(borrower, 'rejected')
            flash('Borrower rejected.', 'warning')

        db.session.commit()

    return redirect(url_for('borrowers.view', id=borrower.id))


@borrowers_bp.route('/<uuid:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    borrower = Borrower.query.get_or_404(id)

    # Check for active loans
    if borrower.active_loans:
        flash('Cannot delete borrower with active loans.', 'danger')
        return redirect(url_for('borrowers.view', id=borrower.id))

    borrower.is_deleted = True
    db.session.commit()

    log_borrower_action(borrower, 'deleted')

    flash('Borrower deleted.', 'info')
    return redirect(url_for('borrowers.index'))


@borrowers_bp.route('/<uuid:id>/link-user', methods=['POST'])
@login_required
@role_required('Admin', 'CreditOfficer')
def link_user(id):
    borrower = Borrower.query.get_or_404(id)
    form = LinkUserForm()

    if form.validate_on_submit():
        user = User.query.filter(User.email.ilike(form.user_email.data)).first()

        if not user:
            flash('No user found with that email address.', 'danger')
            return redirect(url_for('borrowers.view', id=borrower.id))

        if user.borrower_profile:
            flash('That user is already linked to another borrower.', 'danger')
            return redirect(url_for('borrowers.view', id=borrower.id))

        if borrower.user_id:
            flash('This borrower is already linked to a user account.', 'danger')
            return redirect(url_for('borrowers.view', id=borrower.id))

        borrower.user_id = user.id
        db.session.commit()

        log_borrower_action(borrower, 'linked_user', new_values={'user_email': user.email})

        flash(f'Successfully linked user account ({user.email}) to this borrower.', 'success')

    return redirect(url_for('borrowers.view', id=borrower.id))


@borrowers_bp.route('/<uuid:id>/unlink-user', methods=['POST'])
@login_required
@role_required('Admin')
def unlink_user(id):
    borrower = Borrower.query.get_or_404(id)

    if not borrower.user_id:
        flash('This borrower is not linked to any user account.', 'warning')
        return redirect(url_for('borrowers.view', id=borrower.id))

    old_email = borrower.user.email if borrower.user else 'Unknown'
    borrower.user_id = None
    db.session.commit()

    log_borrower_action(borrower, 'unlinked_user', old_values={'user_email': old_email})

    flash('User account unlinked from this borrower.', 'info')
    return redirect(url_for('borrowers.view', id=borrower.id))
