from flask import request
from flask_login import current_user
from ..models.audit import AuditLog
from ..extensions import db


def log_action(entity_type, entity_id, action, old_values=None, new_values=None):
    """Log an auditable action."""
    user_id = current_user.id if current_user and current_user.is_authenticated else None
    ip_address = request.remote_addr if request else None
    user_agent = request.user_agent.string if request and request.user_agent else None

    log_entry = AuditLog.log(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id=user_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent
    )
    return log_entry


def log_loan_action(loan, action, old_values=None, new_values=None):
    """Log a loan-related action."""
    return log_action('Loan', loan.id, action, old_values, new_values)


def log_payment_action(payment, action, old_values=None, new_values=None):
    """Log a payment-related action."""
    return log_action('Payment', payment.id, action, old_values, new_values)


def log_borrower_action(borrower, action, old_values=None, new_values=None):
    """Log a borrower-related action."""
    return log_action('Borrower', borrower.id, action, old_values, new_values)


def log_property_action(property_obj, action, old_values=None, new_values=None):
    """Log a property-related action."""
    return log_action('Property', property_obj.id, action, old_values, new_values)


def log_document_action(document, action, old_values=None, new_values=None):
    """Log a document-related action."""
    return log_action('Document', document.id, action, old_values, new_values)


def log_user_action(user, action, old_values=None, new_values=None):
    """Log a user-related action."""
    return log_action('User', user.id, action, old_values, new_values)


def get_entity_audit_trail(entity_type, entity_id, limit=50):
    """Get audit trail for a specific entity."""
    return AuditLog.query.filter_by(
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
