import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSON
from ..extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    old_values = db.Column(JSON)
    new_values = db.Column(JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))

    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.entity_type}:{self.entity_id}>'

    @classmethod
    def log(cls, entity_type, entity_id, action, user_id=None, old_values=None,
            new_values=None, ip_address=None, user_agent=None):
        log_entry = cls(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log_entry)
        return log_entry
