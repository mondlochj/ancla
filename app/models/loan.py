import uuid
from enum import Enum
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy.dialects.postgresql import UUID
from ..extensions import db


class LoanStatus(str, Enum):
    DRAFT = 'Draft'
    UNDER_REVIEW = 'UnderReview'
    APPROVED = 'Approved'
    ACTIVE = 'Active'
    MATURED = 'Matured'
    DEFAULTED = 'Defaulted'
    LEGAL_READY = 'LegalReady'
    CLOSED = 'Closed'


# Valid status transitions
LOAN_STATUS_TRANSITIONS = {
    LoanStatus.DRAFT.value: [LoanStatus.UNDER_REVIEW.value],
    LoanStatus.UNDER_REVIEW.value: [LoanStatus.APPROVED.value, LoanStatus.DRAFT.value],
    LoanStatus.APPROVED.value: [LoanStatus.ACTIVE.value],
    LoanStatus.ACTIVE.value: [LoanStatus.MATURED.value, LoanStatus.DEFAULTED.value, LoanStatus.CLOSED.value],
    LoanStatus.MATURED.value: [LoanStatus.DEFAULTED.value, LoanStatus.CLOSED.value],
    LoanStatus.DEFAULTED.value: [LoanStatus.LEGAL_READY.value, LoanStatus.CLOSED.value],
    LoanStatus.LEGAL_READY.value: [LoanStatus.CLOSED.value],
    LoanStatus.CLOSED.value: []
}


class LoanProduct(db.Model):
    __tablename__ = 'loan_products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    min_amount = db.Column(db.Numeric(14, 2), default=10000)
    max_amount = db.Column(db.Numeric(14, 2), default=1000000)

    min_term_months = db.Column(db.Integer, default=3)
    max_term_months = db.Column(db.Integer, default=6)

    interest_rate = db.Column(db.Numeric(5, 4), default=0.10)  # 10% monthly
    max_ltv = db.Column(db.Numeric(5, 4), default=0.40)  # 40%
    late_fee_rate = db.Column(db.Numeric(5, 4), default=0.05)  # 5%

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship('Loan', back_populates='product', lazy='dynamic')

    def __repr__(self):
        return f'<LoanProduct {self.name}>'

    @staticmethod
    def insert_default_products():
        products = [
            {
                'name': 'Standard Land Loan',
                'description': 'Short-term loan secured by land (Promesa de Compraventa)',
                'min_amount': 10000,
                'max_amount': 500000,
                'min_term_months': 3,
                'max_term_months': 6,
                'interest_rate': 0.10,
                'max_ltv': 0.40,
                'late_fee_rate': 0.05
            },
            {
                'name': 'Premium Land Loan',
                'description': 'Higher value loans for established borrowers',
                'min_amount': 100000,
                'max_amount': 2000000,
                'min_term_months': 3,
                'max_term_months': 6,
                'interest_rate': 0.08,
                'max_ltv': 0.35,
                'late_fee_rate': 0.05
            }
        ]

        for prod_data in products:
            product = LoanProduct.query.filter_by(name=prod_data['name']).first()
            if product is None:
                product = LoanProduct(**prod_data)
                db.session.add(product)
        db.session.commit()


class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_number = db.Column(db.String(20), unique=True, nullable=False)

    borrower_id = db.Column(UUID(as_uuid=True), db.ForeignKey('borrowers.id'), nullable=False)
    property_id = db.Column(UUID(as_uuid=True), db.ForeignKey('properties.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('loan_products.id'), nullable=False)

    # Loan terms
    loan_amount = db.Column(db.Numeric(14, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 4), nullable=False)  # Monthly rate
    term_months = db.Column(db.Integer, nullable=False)
    ltv = db.Column(db.Numeric(5, 4), nullable=False)

    # Status
    status = db.Column(db.String(20), default=LoanStatus.DRAFT.value, index=True)

    # Dates
    application_date = db.Column(db.Date, default=date.today)
    approved_at = db.Column(db.DateTime)
    disbursement_date = db.Column(db.Date)
    maturity_date = db.Column(db.Date)

    # Approval
    approved_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    approval_notes = db.Column(db.Text)

    # Creation
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    borrower = db.relationship('Borrower', back_populates='loans')
    collateral = db.relationship('Property', back_populates='loans')
    product = db.relationship('LoanProduct', back_populates='loans')
    approver = db.relationship('User', foreign_keys=[approved_by], back_populates='approved_loans')
    creator = db.relationship('User', foreign_keys=[created_by], back_populates='created_loans')
    documents = db.relationship('Document', back_populates='loan', lazy='dynamic',
                               cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='loan', lazy='dynamic')
    schedule = db.relationship('PaymentSchedule', back_populates='loan', lazy='dynamic')
    collection_actions = db.relationship('CollectionAction', back_populates='loan', lazy='dynamic')

    def __repr__(self):
        return f'<Loan {self.loan_number}>'

    @staticmethod
    def generate_loan_number():
        today = date.today()
        prefix = f'ANC-{today.year}{today.month:02d}'
        last_loan = Loan.query.filter(
            Loan.loan_number.like(f'{prefix}%')
        ).order_by(Loan.loan_number.desc()).first()

        if last_loan:
            last_num = int(last_loan.loan_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f'{prefix}-{new_num:04d}'

    def can_transition_to(self, new_status):
        allowed = LOAN_STATUS_TRANSITIONS.get(self.status, [])
        return new_status in allowed

    def transition_to(self, new_status):
        if not self.can_transition_to(new_status):
            raise ValueError(f'Cannot transition from {self.status} to {new_status}')
        self.status = new_status

    @property
    def monthly_interest(self):
        return self.loan_amount * self.interest_rate

    @property
    def total_interest(self):
        return self.monthly_interest * self.term_months

    @property
    def total_repayment(self):
        return self.loan_amount + self.total_interest

    @property
    def outstanding_principal(self):
        from .payment import Payment, PaymentType
        paid = db.session.query(
            db.func.coalesce(db.func.sum(Payment.amount), 0)
        ).filter(
            Payment.loan_id == self.id,
            Payment.payment_type == PaymentType.PRINCIPAL.value
        ).scalar()
        return self.loan_amount - paid

    @property
    def outstanding_interest(self):
        from .payment import Payment, PaymentType
        total_interest_due = sum(s.interest_due for s in self.schedule if s.due_date <= date.today())
        paid = db.session.query(
            db.func.coalesce(db.func.sum(Payment.amount), 0)
        ).filter(
            Payment.loan_id == self.id,
            Payment.payment_type == PaymentType.INTEREST.value
        ).scalar()
        return total_interest_due - paid

    @property
    def days_past_due(self):
        unpaid_schedule = self.schedule.filter_by(is_paid=False).first()
        if unpaid_schedule and unpaid_schedule.due_date < date.today():
            return (date.today() - unpaid_schedule.due_date).days
        return 0

    def all_documents_complete(self):
        from .document import DocumentType, ExecutionStatus
        required_docs = [
            DocumentType.MUTUO_MERCANTIL.value,
            DocumentType.PAGARE.value,
            DocumentType.PROMESA_COMPRAVENTA.value
        ]
        for doc_type in required_docs:
            doc = self.documents.filter_by(document_type=doc_type).first()
            if not doc or doc.execution_status != ExecutionStatus.EXECUTED.value:
                return False
        return True

    def get_document_checklist(self):
        """Return checklist of required documents with their status."""
        from .document import DocumentType, ExecutionStatus

        required_docs = [
            (DocumentType.MUTUO_MERCANTIL.value, 'Mutuo Mercantil', 'Loan agreement contract'),
            (DocumentType.PAGARE.value, 'Pagaré', 'Promissory note'),
            (DocumentType.PROMESA_COMPRAVENTA.value, 'Promesa de Compraventa', 'Property sale promise agreement'),
        ]

        checklist = []
        for doc_type, display_name, description in required_docs:
            doc = self.documents.filter_by(document_type=doc_type).first()
            if doc:
                status = doc.execution_status
                is_complete = (status == ExecutionStatus.EXECUTED.value)
            else:
                status = 'Not Uploaded'
                is_complete = False

            checklist.append({
                'type': doc_type,
                'name': display_name,
                'description': description,
                'status': status,
                'is_complete': is_complete,
                'document': doc
            })

        return checklist

    def calculate_maturity_date(self, start_date=None):
        if start_date is None:
            start_date = date.today()
        return start_date + relativedelta(months=self.term_months)
