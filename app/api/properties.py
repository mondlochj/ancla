"""
Properties (Collateral) API endpoints.

Provides CRUD operations for properties.
"""

from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_

from . import api_bp
from app.extensions import db
from app.models import Property, User
from app.schemas import PropertySchema, PropertyCreateSchema


property_schema = PropertySchema()
properties_schema = PropertySchema(many=True)


def check_internal_user():
    """Check if current user is an internal user (not borrower)."""
    user = User.query.get(get_jwt_identity())
    if not user or user.role.name == 'Borrower':
        return None
    return user


@api_bp.route('/properties', methods=['GET'])
@jwt_required()
def get_properties():
    """Get paginated list of properties with optional filters."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    verification_status = request.args.get('verificationStatus')
    department = request.args.get('department')
    search = request.args.get('search', '')

    # Build query
    query = Property.query

    if verification_status:
        query = query.filter(Property.verification_status == verification_status)

    if department:
        query = query.filter(Property.department == department)

    if search:
        query = query.filter(
            or_(
                Property.finca.ilike(f'%{search}%'),
                Property.folio.ilike(f'%{search}%'),
                Property.libro.ilike(f'%{search}%'),
                Property.address.ilike(f'%{search}%'),
            )
        )

    # Order by created date
    query = query.order_by(Property.created_at.desc())

    # Paginate
    total = query.count()
    properties = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'data': properties_schema.dump(properties),
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': (total + page_size - 1) // page_size,
    }), 200


@api_bp.route('/properties', methods=['POST'])
@jwt_required()
def create_property():
    """Create a new property."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        data = PropertyCreateSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400

    # Check if property with same finca/folio/libro exists
    existing = Property.query.filter_by(
        finca=data['finca'],
        folio=data['folio'],
        libro=data['libro']
    ).first()
    if existing:
        return jsonify({'message': 'A property with this Finca/Folio/Libro already exists'}), 409

    # Create property
    property = Property(
        finca=data['finca'],
        folio=data['folio'],
        libro=data['libro'],
        address=data['address'],
        municipality=data['municipality'],
        department=data['department'],
        area_m2=data['area_m2'],
        market_value=data['market_value'],
        appraisal_value=data.get('appraisal_value'),
        appraisal_date=data.get('appraisal_date'),
        verification_status='Pending',
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        notes=data.get('notes'),
    )
    db.session.add(property)
    db.session.commit()

    return jsonify(property_schema.dump(property)), 201


@api_bp.route('/properties/<property_id>', methods=['GET'])
@jwt_required()
def get_property(property_id):
    """Get property details by ID."""
    user = check_internal_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 403

    property = Property.query.get(property_id)
    if not property:
        return jsonify({'message': 'Property not found'}), 404

    return jsonify(property_schema.dump(property)), 200


@api_bp.route('/properties/<property_id>', methods=['PUT'])
@jwt_required()
def update_property(property_id):
    """Update property details."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    property = Property.query.get(property_id)
    if not property:
        return jsonify({'message': 'Property not found'}), 404

    data = request.get_json()

    # Update fields
    if 'address' in data:
        property.address = data['address']
    if 'municipality' in data:
        property.municipality = data['municipality']
    if 'department' in data:
        property.department = data['department']
    if 'areaM2' in data:
        property.area_m2 = data['areaM2']
    if 'marketValue' in data:
        property.market_value = data['marketValue']
    if 'appraisalValue' in data:
        property.appraisal_value = data['appraisalValue']
    if 'appraisalDate' in data:
        property.appraisal_date = data['appraisalDate']
    if 'latitude' in data:
        property.latitude = data['latitude']
    if 'longitude' in data:
        property.longitude = data['longitude']
    if 'notes' in data:
        property.notes = data['notes']

    property.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(property_schema.dump(property)), 200


@api_bp.route('/properties/<property_id>/verify', methods=['POST'])
@jwt_required()
def verify_property(property_id):
    """Verify a property."""
    user = check_internal_user()
    if not user or user.role.name not in ['Admin', 'CreditOfficer']:
        return jsonify({'message': 'Unauthorized'}), 403

    property = Property.query.get(property_id)
    if not property:
        return jsonify({'message': 'Property not found'}), 404

    data = request.get_json() or {}
    status = data.get('status', 'Verified')

    if status not in ['Verified', 'Rejected']:
        return jsonify({'message': 'Invalid status'}), 400

    property.verification_status = status
    property.verified_by_id = user.id
    property.verified_at = datetime.utcnow()
    property.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(property_schema.dump(property)), 200
