import uuid
from enum import Enum
from datetime import datetime, date
from sqlalchemy.dialects.postgresql import UUID
from ..extensions import db


class PaymentType(str, Enum):
    INTEREST = 'Interest'
    PRINCIPAL = 'Principal'
    LATE_FEE = 'LateFee'
    OTHER = 'Other'


class PaymentSchedule(db.Model):
    __tablename__ = 'payment_schedule'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('loans.id'), nullable=False)

    payment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False, index=True)

    principal_due = db.Column(db.Numeric(14, 2), default=0)
    interest_due = db.Column(db.Numeric(14, 2), nullable=False)

    is_paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.Date)
    late_fee = db.Column(db.Numeric(14, 2), default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    loan = db.relationship('Loan', back_populates='schedule')
    payments = db.relationship('Payment', back_populates='schedule_item', lazy='dynamic')

    def __repr__(self):
        return f'<PaymentSchedule #{self.payment_number} for Loan {self.loan_id}>'

    @property
    def total_due(self):
        return self.principal_due + self.interest_due + self.late_fee

    @property
    def is_overdue(self):
        return not self.is_paid and self.due_date < date.today()

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0

    def calculate_late_fee(self, late_fee_rate):
        if self.is_overdue and self.late_fee == 0:
            self.late_fee = (self.principal_due + self.interest_due) * late_fee_rate
        return self.late_fee

    def mark_paid(self, paid_date=None):
        self.is_paid = True
        self.paid_date = paid_date or date.today()


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('loans.id'), nullable=False)
    schedule_id = db.Column(UUID(as_uuid=True), db.ForeignKey('payment_schedule.id'), nullable=True)

    amount = db.Column(db.Numeric(14, 2), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)

    payment_method = db.Column(db.String(50))  # Cash, Transfer, Check
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)

    recorded_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loan = db.relationship('Loan', back_populates='payments')
    schedule_item = db.relationship('PaymentSchedule', back_populates='payments')
    recorder = db.relationship('User')

    def __repr__(self):
        return f'<Payment {self.amount} for Loan {self.loan_id}>'
