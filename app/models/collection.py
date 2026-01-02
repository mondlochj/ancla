import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from ..extensions import db


class CollectionStage(str, Enum):
    CURRENT = 'Current'
    REMINDER = 'Reminder'
    GRACE = 'Grace'
    DELINQUENT = 'Delinquent'
    LEGAL_READY = 'LegalReady'


class ActionType(str, Enum):
    PHONE_CALL = 'PhoneCall'
    SMS = 'SMS'
    EMAIL = 'Email'
    VISIT = 'Visit'
    LETTER = 'Letter'
    EXTENSION_GRANTED = 'ExtensionGranted'
    PAYMENT_PROMISE = 'PaymentPromise'
    LEGAL_NOTICE = 'LegalNotice'
    NOTE = 'Note'


class CollectionAction(db.Model):
    __tablename__ = 'collection_actions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('loans.id'), nullable=False)

    stage = db.Column(db.String(20), nullable=False)
    action_type = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.Text)

    # Contact info
    contact_name = db.Column(db.String(200))
    contact_phone = db.Column(db.String(20))
    contact_result = db.Column(db.String(100))

    # Extension tracking
    extension_granted = db.Column(db.Boolean, default=False)
    extension_days = db.Column(db.Integer)
    new_due_date = db.Column(db.Date)

    # Payment promise
    promise_amount = db.Column(db.Numeric(14, 2))
    promise_date = db.Column(db.Date)
    promise_kept = db.Column(db.Boolean)

    # Legal escalation
    escalated_to_legal = db.Column(db.Boolean, default=False)
    escalation_date = db.Column(db.DateTime)

    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    loan = db.relationship('Loan', back_populates='collection_actions')
    creator = db.relationship('User')

    def __repr__(self):
        return f'<CollectionAction {self.action_type} for Loan {self.loan_id}>'

    @classmethod
    def determine_stage(cls, days_past_due, grace_period=5):
        if days_past_due <= 0:
            return CollectionStage.CURRENT.value
        elif days_past_due <= grace_period:
            return CollectionStage.GRACE.value
        elif days_past_due <= 15:
            return CollectionStage.REMINDER.value
        elif days_past_due <= 30:
            return CollectionStage.DELINQUENT.value
        else:
            return CollectionStage.LEGAL_READY.value
