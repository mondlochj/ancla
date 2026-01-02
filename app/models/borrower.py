import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from ..extensions import db


class VerificationStatus(str, Enum):
    PENDING = 'Pending'
    IN_PROGRESS = 'InProgress'
    VERIFIED = 'Verified'
    REJECTED = 'Rejected'


class RiskTier(str, Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'


class Borrower(db.Model):
    __tablename__ = 'borrowers'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), unique=True, nullable=True)

    # Identity
    full_name = db.Column(db.String(200), nullable=False)
    dpi = db.Column(db.String(20), nullable=False)  # Documento Personal de Identificacion
    nit = db.Column(db.String(20))  # Numero de Identificacion Tributaria

    # Contact
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    department = db.Column(db.String(50))
    municipality = db.Column(db.String(100))

    # Employment / Business
    employment_type = db.Column(db.String(50))  # Employee, SelfEmployed, Business
    employer_name = db.Column(db.String(200))
    business_name = db.Column(db.String(200))
    monthly_income = db.Column(db.Numeric(12, 2))

    # Verification
    verification_status = db.Column(db.String(20), default=VerificationStatus.PENDING.value)
    verified_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime)
    verification_notes = db.Column(db.Text)

    # Risk
    risk_tier = db.Column(db.String(20), default=RiskTier.MEDIUM.value)

    # Metadata
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], back_populates='borrower_profile')
    verifier = db.relationship('User', foreign_keys=[verified_by])
    properties = db.relationship('Property', back_populates='borrower', lazy='dynamic')
    loans = db.relationship('Loan', back_populates='borrower', lazy='dynamic')

    def __repr__(self):
        return f'<Borrower {self.full_name}>'

    @property
    def is_verified(self):
        return self.verification_status == VerificationStatus.VERIFIED.value

    @property
    def masked_dpi(self):
        if self.dpi and len(self.dpi) >= 4:
            return '*' * (len(self.dpi) - 4) + self.dpi[-4:]
        return '****'

    @property
    def active_loans(self):
        from .loan import LoanStatus
        return self.loans.filter(Loan.status.in_([
            LoanStatus.ACTIVE.value,
            LoanStatus.MATURED.value,
            LoanStatus.DEFAULTED.value
        ])).all()

    def verify(self, user, notes=None):
        self.verification_status = VerificationStatus.VERIFIED.value
        self.verified_by = user.id
        self.verified_at = datetime.utcnow()
        if notes:
            self.verification_notes = notes

    def reject(self, user, notes=None):
        self.verification_status = VerificationStatus.REJECTED.value
        self.verified_by = user.id
        self.verified_at = datetime.utcnow()
        if notes:
            self.verification_notes = notes
