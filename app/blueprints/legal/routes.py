import os
from flask import render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import login_required, current_user
from . import legal_bp
from .forms import DocumentUploadForm, DocumentAcceptanceForm
from ...models.document import Document, ExecutionStatus
from ...models.loan import Loan
from ...extensions import db
from ...utils.decorators import internal_only, role_required
from ...utils.helpers import save_uploaded_file, get_file_path
from ...services.audit_service import log_document_action


@legal_bp.route('/')
@login_required
@internal_only
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')

    query = Document.query

    if status_filter:
        query = query.filter_by(execution_status=status_filter)

    documents = query.order_by(Document.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('legal/index.html',
                          documents=documents,
                          status_filter=status_filter)


@legal_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    loan_id = request.args.get('loan_id')
    doc_type = request.args.get('doc_type')
    loan = None
    if loan_id:
        loan = Loan.query.get_or_404(loan_id)

    # Check permissions: internal users or borrower for their own loan
    if current_user.role.name == 'Borrower':
        if not loan or not current_user.borrower_profile or \
           loan.borrower_id != current_user.borrower_profile.id:
            abort(403)
        # Borrowers can only upload before loan is active
        if loan.status not in ['Draft', 'UnderReview', 'Approved']:
            flash('Cannot upload documents for this loan.', 'warning')
            return redirect(url_for('loans.my_loans'))
    elif current_user.role.name not in ['Admin', 'CreditOfficer', 'Legal']:
        abort(403)

    form = DocumentUploadForm()

    # Pre-select document type if passed
    if doc_type and request.method == 'GET':
        form.document_type.data = doc_type

    if form.validate_on_submit():
        if not loan_id:
            flash('Loan is required.', 'danger')
            return redirect(url_for('legal.upload'))

        file_path = save_uploaded_file(form.file.data, 'documents')

        document = Document(
            loan_id=loan_id,
            document_type=form.document_type.data,
            name=form.name.data,
            description=form.description.data,
            file_path=file_path,
            file_size=form.file.data.seek(0, 2) or 0,
            mime_type='application/pdf',
            execution_status=ExecutionStatus.UPLOADED.value,
            uploaded_by=current_user.id
        )

        db.session.add(document)
        db.session.commit()

        log_document_action(document, 'uploaded')

        flash('Document uploaded successfully.', 'success')

        # Redirect borrowers to my_loans, others to loan view
        if current_user.role.name == 'Borrower':
            return redirect(url_for('loans.borrower_loan_view', id=loan_id))
        return redirect(url_for('loans.view', id=loan_id))

    return render_template('legal/upload.html', form=form, loan=loan)


@legal_bp.route('/<uuid:id>')
@login_required
def view(id):
    document = Document.query.get_or_404(id)

    # Borrowers can only view their own loan documents
    if current_user.role.name == 'Borrower':
        if not current_user.borrower_profile or \
           document.loan.borrower_id != current_user.borrower_profile.id:
            abort(403)

    acceptance_form = DocumentAcceptanceForm()
    return render_template('legal/view.html',
                          document=document,
                          acceptance_form=acceptance_form)


@legal_bp.route('/<uuid:id>/download')
@login_required
def download(id):
    document = Document.query.get_or_404(id)

    # Borrowers can only download their own documents
    if current_user.role.name == 'Borrower':
        if not current_user.borrower_profile or \
           document.loan.borrower_id != current_user.borrower_profile.id:
            abort(403)

    file_path = get_file_path(document.file_path)
    if not file_path or not os.path.exists(file_path):
        flash('File not found.', 'danger')
        return redirect(url_for('legal.view', id=id))

    return send_file(file_path, as_attachment=True,
                    download_name=f'{document.name}.pdf')


@legal_bp.route('/<uuid:id>/mark-sent', methods=['POST'])
@login_required
@role_required('Admin', 'Legal')
def mark_sent(id):
    document = Document.query.get_or_404(id)

    document.execution_status = ExecutionStatus.SENT.value
    db.session.commit()

    log_document_action(document, 'marked_sent')

    flash('Document marked as sent.', 'success')
    return redirect(url_for('legal.view', id=id))


@legal_bp.route('/<uuid:id>/mark-executed', methods=['POST'])
@login_required
@role_required('Admin', 'Legal')
def mark_executed(id):
    document = Document.query.get_or_404(id)

    document.execution_status = ExecutionStatus.EXECUTED.value
    db.session.commit()

    log_document_action(document, 'marked_executed')

    flash('Document marked as executed.', 'success')
    return redirect(url_for('legal.view', id=id))


@legal_bp.route('/<uuid:id>/accept', methods=['POST'])
@login_required
def accept(id):
    """Borrower digital acceptance of document."""
    document = Document.query.get_or_404(id)

    # Only borrowers can accept documents for their own loans
    if current_user.role.name != 'Borrower':
        flash('Only borrowers can digitally accept documents.', 'warning')
        return redirect(url_for('legal.view', id=id))

    if not current_user.borrower_profile or \
       document.loan.borrower_id != current_user.borrower_profile.id:
        abort(403)

    document.accept(
        user=current_user,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None
    )
    db.session.commit()

    log_document_action(document, 'digitally_accepted', new_values={
        'accepted_ip': document.accepted_ip,
        'accepted_at': str(document.accepted_at)
    })

    flash('Document accepted successfully.', 'success')
    return redirect(url_for('legal.view', id=id))
