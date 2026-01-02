from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import collateral_bp
from .forms import PropertyForm, PropertyPhotoForm, PropertyVerificationForm
from ...models.property import Property, PropertyPhoto
from ...models.borrower import Borrower
from ...extensions import db
from ...utils.decorators import internal_only, role_required
from ...utils.helpers import save_uploaded_file, allowed_document, allowed_image
from ...services.audit_service import log_property_action


@collateral_bp.route('/')
@login_required
@internal_only
def index():
    page = request.args.get('page', 1, type=int)
    verified_filter = request.args.get('verified', '')
    department_filter = request.args.get('department', '')
    search = request.args.get('search', '')

    query = Property.query

    if verified_filter == 'yes':
        query = query.filter_by(verified=True)
    elif verified_filter == 'no':
        query = query.filter_by(verified=False)

    if department_filter:
        query = query.filter_by(department=department_filter)

    if search:
        query = query.join(Borrower).filter(
            db.or_(
                Borrower.full_name.ilike(f'%{search}%'),
                Borrower.dpi.ilike(f'%{search}%'),
                Borrower.email.ilike(f'%{search}%'),
                Property.finca.ilike(f'%{search}%'),
                Property.municipality.ilike(f'%{search}%')
            )
        )

    properties = query.order_by(Property.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('collateral/index.html',
                          properties=properties,
                          verified_filter=verified_filter,
                          department_filter=department_filter,
                          search=search)


@collateral_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'CreditOfficer')
def create():
    borrower_id = request.args.get('borrower_id')
    borrower = None
    if borrower_id:
        borrower = Borrower.query.get_or_404(borrower_id)

    form = PropertyForm()

    if form.validate_on_submit():
        if not borrower_id:
            flash('Borrower is required.', 'danger')
            return redirect(url_for('collateral.create'))

        property_obj = Property(
            borrower_id=borrower_id,
            property_type=form.property_type.data,
            finca=form.finca.data,
            folio=form.folio.data,
            libro=form.libro.data,
            department=form.department.data,
            municipality=form.municipality.data,
            address=form.address.data,
            market_value=form.market_value.data,
            appraised_value=form.appraised_value.data,
            appraisal_date=form.appraisal_date.data,
            appraised_by=form.appraised_by.data
        )

        # Set GPS coordinates if provided
        if form.latitude.data and form.longitude.data:
            property_obj.set_location(float(form.latitude.data), float(form.longitude.data))

        # Handle title PDF upload
        if form.title_pdf.data:
            file_path = save_uploaded_file(form.title_pdf.data, 'documents')
            property_obj.title_pdf_path = file_path

        db.session.add(property_obj)
        db.session.commit()

        log_property_action(property_obj, 'created')

        flash('Property added successfully.', 'success')
        return redirect(url_for('collateral.view', id=property_obj.id))

    return render_template('collateral/form.html', form=form, borrower=borrower,
                          title='Add Property')


@collateral_bp.route('/<uuid:id>')
@login_required
@internal_only
def view(id):
    property_obj = Property.query.get_or_404(id)
    photo_form = PropertyPhotoForm()
    verification_form = PropertyVerificationForm()
    return render_template('collateral/view.html',
                          property=property_obj,
                          photo_form=photo_form,
                          verification_form=verification_form)


@collateral_bp.route('/<uuid:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'CreditOfficer')
def edit(id):
    property_obj = Property.query.get_or_404(id)
    form = PropertyForm(obj=property_obj)

    # Populate coordinates if available
    coords = property_obj.get_coordinates()
    if coords and not form.latitude.data:
        form.latitude.data = coords['latitude']
        form.longitude.data = coords['longitude']

    if form.validate_on_submit():
        old_values = {
            'market_value': str(property_obj.market_value),
            'verified': property_obj.verified
        }

        property_obj.property_type = form.property_type.data
        property_obj.finca = form.finca.data
        property_obj.folio = form.folio.data
        property_obj.libro = form.libro.data
        property_obj.department = form.department.data
        property_obj.municipality = form.municipality.data
        property_obj.address = form.address.data
        property_obj.market_value = form.market_value.data
        property_obj.appraised_value = form.appraised_value.data
        property_obj.appraisal_date = form.appraisal_date.data
        property_obj.appraised_by = form.appraised_by.data

        if form.latitude.data and form.longitude.data:
            property_obj.set_location(float(form.latitude.data), float(form.longitude.data))

        if form.title_pdf.data:
            file_path = save_uploaded_file(form.title_pdf.data, 'documents')
            property_obj.title_pdf_path = file_path

        db.session.commit()

        log_property_action(property_obj, 'updated', old_values=old_values)

        flash('Property updated successfully.', 'success')
        return redirect(url_for('collateral.view', id=property_obj.id))

    return render_template('collateral/form.html', form=form, property=property_obj,
                          borrower=property_obj.borrower, title='Edit Property')


@collateral_bp.route('/<uuid:id>/verify', methods=['POST'])
@login_required
@role_required('Admin', 'Legal')
def verify(id):
    property_obj = Property.query.get_or_404(id)
    form = PropertyVerificationForm()

    if form.validate_on_submit():
        property_obj.verify_property(current_user, form.verification_notes.data)
        db.session.commit()

        log_property_action(property_obj, 'verified')

        flash('Property verified successfully.', 'success')

    return redirect(url_for('collateral.view', id=property_obj.id))


@collateral_bp.route('/<uuid:id>/photos', methods=['POST'])
@login_required
@role_required('Admin', 'CreditOfficer', 'Legal')
def add_photo(id):
    property_obj = Property.query.get_or_404(id)
    form = PropertyPhotoForm()

    if form.validate_on_submit():
        file_path = save_uploaded_file(form.photo.data, 'photos')

        photo = PropertyPhoto(
            property_id=property_obj.id,
            file_path=file_path,
            description=form.description.data,
            uploaded_by=current_user.id
        )
        db.session.add(photo)
        db.session.commit()

        flash('Photo uploaded successfully.', 'success')

    return redirect(url_for('collateral.view', id=property_obj.id))
