import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from ..extensions import db


class DocumentType(str, Enum):
    MUTUO_MERCANTIL = 'MutuoMercantil'
    PAGARE = 'Pagare'
    PROMESA_COMPRAVENTA = 'PromesaCompraventa'
    ANNEX = 'Annex'
    DPI_COPY = 'DPICopy'
    PROOF_OF_INCOME = 'ProofOfIncome'
    PROPERTY_TITLE = 'PropertyTitle'
    APPRAISAL = 'Appraisal'
    OTHER = 'Other'


class ExecutionStatus(str, Enum):
    PENDING = 'Pending'
    UPLOADED = 'Uploaded'
    SENT = 'Sent'
    EXECUTED = 'Executed'
    REJECTED = 'Rejected'


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('loans.id'), nullable=False)

    document_type = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # File info
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))

    # Versioning
    version = db.Column(db.Integer, default=1)
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey('documents.id'), nullable=True)

    # Status
    execution_status = db.Column(db.String(20), default=ExecutionStatus.PENDING.value)

    # Digital acceptance metadata
    accepted_at = db.Column(db.DateTime)
    accepted_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    accepted_ip = db.Column(db.String(45))
    accepted_user_agent = db.Column(db.String(500))

    # Upload info
    uploaded_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loan = db.relationship('Loan', back_populates='documents')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    accepter = db.relationship('User', foreign_keys=[accepted_by])
    parent = db.relationship('Document', remote_side=[id], backref='versions')

    def __repr__(self):
        return f'<Document {self.document_type} for Loan {self.loan_id}>'

    def accept(self, user, ip_address, user_agent):
        self.execution_status = ExecutionStatus.EXECUTED.value
        self.accepted_at = datetime.utcnow()
        self.accepted_by = user.id
        self.accepted_ip = ip_address
        self.accepted_user_agent = user_agent

    def create_new_version(self, file_path, uploaded_by):
        new_doc = Document(
            loan_id=self.loan_id,
            document_type=self.document_type,
            name=self.name,
            description=self.description,
            file_path=file_path,
            version=self.version + 1,
            parent_id=self.id,
            uploaded_by=uploaded_by
        )
        return new_doc

    @property
    def is_executed(self):
        return self.execution_status == ExecutionStatus.EXECUTED.value

    @property
    def is_legal_document(self):
        return self.document_type in [
            DocumentType.MUTUO_MERCANTIL.value,
            DocumentType.PAGARE.value,
            DocumentType.PROMESA_COMPRAVENTA.value
        ]
