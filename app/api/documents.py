"""
Documents API endpoints.

Provides CRUD operations for legal documents.
"""

from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api_bp
from app.extensions import db
from app.models import Document, Loan, User
from app.schemas import DocumentSchema


document_schema = DocumentSchema()
documents_schema = DocumentSchema(many=True)


def check_internal_user():
    """Check if current user is an internal user (not borrower)."""
    user = User.query.get(get_jwt_identity())
    if not user or user.role.name == 'Borrower':
        return None
    return user


@api_bp.route('/documents', methods=['GET'])
@jwt_required()
def get_documents():
    """Get paginated list of documents with optional filters."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    loan_id = request.args.get('loanId')
    document_type = request.args.get('documentType')
    status = request.args.get('status')

    # Build query
    query = Document.query

    if loan_id:
        query = query.filter(Document.loan_id == loan_id)

    if document_type:
        query = query.filter(Document.document_type == document_type)

    if status:
        query = query.filter(Document.status == status)

    # Order by date
    query = query.order_by(Document.created_at.desc())

    # Paginate
    total = query.count()
    documents = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'data': documents_schema.dump(documents),
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': (total + page_size - 1) // page_size,
    }), 200


@api_bp.route('/documents/<document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get document details by ID."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    # Borrowers can only view their own loan documents
    if user.role.name == 'Borrower':
        from app.models import Borrower
        borrower = Borrower.query.filter_by(user_id=user_id).first()
        if not borrower or str(document.loan.borrower_id) != str(borrower.id):
            return jsonify({'message': 'Unauthorized'}), 403

    return jsonify(document_schema.dump(document)), 200


@api_bp.route('/documents/<document_id>/upload', methods=['POST'])
@jwt_required()
def upload_document(document_id):
    """Upload a document file."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'Legal']:
        return jsonify({'message': 'Unauthorized'}), 403

    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    # Save file
    import os
    from werkzeug.utils import secure_filename
    from flask import current_app

    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
    os.makedirs(upload_path, exist_ok=True)

    # Add timestamp to filename to avoid collisions
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{document_id}_{timestamp}_{filename}"
    file_path = os.path.join(upload_path, unique_filename)
    file.save(file_path)

    # Update document
    document.file_name = filename
    document.file_path = file_path
    document.status = 'Uploaded'
    document.uploaded_by_id = user.id
    document.uploaded_at = datetime.utcnow()
    document.version += 1
    db.session.commit()

    return jsonify(document_schema.dump(document)), 200


@api_bp.route('/documents/<document_id>/accept', methods=['POST'])
@jwt_required()
def accept_document(document_id):
    """Accept/sign a document digitally."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    # For borrower acceptance, verify they own the loan
    if user.role.name == 'Borrower':
        from app.models import Borrower
        borrower = Borrower.query.filter_by(user_id=user_id).first()
        if not borrower or str(document.loan.borrower_id) != str(borrower.id):
            return jsonify({'message': 'Unauthorized'}), 403

    if document.status != 'Uploaded':
        return jsonify({'message': 'Document must be uploaded before acceptance'}), 400

    # Record acceptance
    document.status = 'Executed'
    document.accepted_by_id = user.id
    document.accepted_at = datetime.utcnow()
    document.accepted_ip = request.remote_addr
    db.session.commit()

    return jsonify(document_schema.dump(document)), 200


@api_bp.route('/loans/<loan_id>/documents', methods=['GET'])
@jwt_required()
def get_loan_documents(loan_id):
    """Get all documents for a loan."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    # Borrowers can only view their own loan documents
    if user.role.name == 'Borrower':
        from app.models import Borrower
        borrower = Borrower.query.filter_by(user_id=user_id).first()
        if not borrower or str(loan.borrower_id) != str(borrower.id):
            return jsonify({'message': 'Unauthorized'}), 403

    documents = Document.query.filter_by(loan_id=loan_id).order_by(
        Document.document_type
    ).all()

    return jsonify({'data': documents_schema.dump(documents)}), 200
