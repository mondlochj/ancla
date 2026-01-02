import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from ..extensions import db


class PropertyType(str, Enum):
    LAND = 'Land'
    HOUSE = 'House'
    COMMERCIAL = 'Commercial'
    AGRICULTURAL = 'Agricultural'


class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    borrower_id = db.Column(UUID(as_uuid=True), db.ForeignKey('borrowers.id'), nullable=False)

    # Property type
    property_type = db.Column(db.String(20), default=PropertyType.LAND.value)

    # Registry information (Registro de la Propiedad)
    finca = db.Column(db.String(50), nullable=False)
    folio = db.Column(db.String(50), nullable=False)
    libro = db.Column(db.String(50), nullable=False)

    # Location
    department = db.Column(db.String(50), nullable=False)
    municipality = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    location = db.Column(Geography(geometry_type='POINT', srid=4326))

    # Valuation
    market_value = db.Column(db.Numeric(14, 2), nullable=False)
    appraised_value = db.Column(db.Numeric(14, 2))
    appraisal_date = db.Column(db.Date)
    appraised_by = db.Column(db.String(200))

    # Verification
    verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime)
    verification_notes = db.Column(db.Text)

    # Documents
    title_pdf_path = db.Column(db.String(500))

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    borrower = db.relationship('Borrower', back_populates='properties')
    verifier = db.relationship('User', foreign_keys=[verified_by])
    loans = db.relationship('Loan', back_populates='collateral', lazy='dynamic')
    photos = db.relationship('PropertyPhoto', back_populates='property', lazy='dynamic',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Property {self.finca}/{self.folio}/{self.libro}>'

    @property
    def registry_number(self):
        return f'{self.finca}/{self.folio}/{self.libro}'

    def has_active_loan(self):
        from .loan import Loan, LoanStatus
        return self.loans.filter(Loan.status.in_([
            LoanStatus.ACTIVE.value,
            LoanStatus.APPROVED.value,
            LoanStatus.UNDER_REVIEW.value
        ])).first() is not None

    def verify_property(self, user, notes=None):
        self.verified = True
        self.verified_by = user.id
        self.verified_at = datetime.utcnow()
        if notes:
            self.verification_notes = notes

    def set_location(self, latitude, longitude):
        from geoalchemy2.elements import WKTElement
        self.location = WKTElement(f'POINT({longitude} {latitude})', srid=4326)

    def get_coordinates(self):
        if self.location is None:
            return None
        from geoalchemy2.shape import to_shape
        point = to_shape(self.location)
        return {'latitude': point.y, 'longitude': point.x}


class PropertyPhoto(db.Model):
    __tablename__ = 'property_photos'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = db.Column(UUID(as_uuid=True), db.ForeignKey('properties.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200))
    uploaded_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    property = db.relationship('Property', back_populates='photos')
    uploader = db.relationship('User')
