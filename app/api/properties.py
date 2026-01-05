"""
Properties (Collateral) API endpoints.

Provides CRUD operations for properties.
"""

from flask import request, jsonify
from . import api_bp


@api_bp.route('/properties', methods=['GET'])
def get_properties():
    """
    Get paginated list of properties with optional filters.

    Query parameters:
        - verificationStatus: Filter by verification status
        - department: Filter by department
        - search: Search by finca/folio/libro or address
        - page: Page number (default: 1)
        - pageSize: Items per page (default: 20)
    """
    return jsonify({
        "data": [],
        "total": 0,
        "page": 1,
        "pageSize": 20,
        "totalPages": 0
    }), 200


@api_bp.route('/properties', methods=['POST'])
def create_property():
    """
    Create a new property.
    """
    return jsonify({
        "message": "Create property endpoint - implementation pending"
    }), 501


@api_bp.route('/properties/<property_id>', methods=['GET'])
def get_property(property_id):
    """
    Get property details by ID.
    """
    return jsonify({
        "message": f"Get property {property_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/properties/<property_id>', methods=['PUT'])
def update_property(property_id):
    """
    Update property details.
    """
    return jsonify({
        "message": f"Update property {property_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/properties/<property_id>/verify', methods=['POST'])
def verify_property(property_id):
    """
    Verify a property.
    """
    return jsonify({
        "message": f"Verify property {property_id} endpoint - implementation pending"
    }), 501
