import uuid
from enum import Enum
from datetime import datetime, timedelta
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID, JSON
from ..extensions import db, bcrypt


class RoleName(str, Enum):
    ADMIN = 'Admin'
    CREDIT_OFFICER = 'CreditOfficer'
    LEGAL = 'Legal'
    COLLECTIONS = 'Collections'
    BORROWER = 'Borrower'


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', back_populates='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'

    @staticmethod
    def insert_roles():
        roles = {
            RoleName.ADMIN.value: {
                'description': 'Full system access',
                'permissions': {'all': True}
            },
            RoleName.CREDIT_OFFICER.value: {
                'description': 'Loan creation and approval',
                'permissions': {
                    'borrowers': ['read', 'write'],
                    'loans': ['read', 'write', 'approve'],
                    'collateral': ['read', 'write'],
                    'payments': ['read']
                }
            },
            RoleName.LEGAL.value: {
                'description': 'Document verification',
                'permissions': {
                    'borrowers': ['read'],
                    'loans': ['read'],
                    'collateral': ['read', 'verify'],
                    'documents': ['read', 'write', 'verify']
                }
            },
            RoleName.COLLECTIONS.value: {
                'description': 'Payments and delinquency management',
                'permissions': {
                    'borrowers': ['read'],
                    'loans': ['read'],
                    'payments': ['read', 'write'],
                    'collections': ['read', 'write']
                }
            },
            RoleName.BORROWER.value: {
                'description': 'Read-only loan view',
                'permissions': {
                    'loans': ['read_own'],
                    'payments': ['read_own'],
                    'documents': ['read_own', 'accept']
                }
            }
        }

        for role_name, role_data in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(
                    name=role_name,
                    description=role_data['description'],
                    permissions=role_data['permissions']
                )
                db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(200))
    token_expires = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    role = db.relationship('Role', back_populates='users')

    # Relationships
    borrower_profile = db.relationship('Borrower', foreign_keys='Borrower.user_id',
                                       back_populates='user', uselist=False)
    approved_loans = db.relationship('Loan', foreign_keys='Loan.approved_by',
                                     back_populates='approver', lazy='dynamic')
    created_loans = db.relationship('Loan', foreign_keys='Loan.created_by',
                                    back_populates='creator', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.email

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_verification_token(self):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        self.verification_token = s.dumps(self.email, salt='email-verification')
        self.token_expires = datetime.utcnow() + timedelta(hours=24)
        return self.verification_token

    @staticmethod
    def verify_token(token, expiration=86400):
        from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt='email-verification', max_age=expiration)
        except (SignatureExpired, BadSignature):
            return None
        return User.query.filter_by(email=email).first()

    def has_role(self, *role_names):
        return self.role.name in role_names

    def is_admin(self):
        return self.role.name == RoleName.ADMIN.value

    def can(self, resource, action):
        if self.is_admin():
            return True
        permissions = self.role.permissions or {}
        if resource in permissions:
            return action in permissions[resource]
        return False
