"""
Borrowers API endpoints.

Provides CRUD operations for borrowers.
"""

from flask import request, jsonify
from . import api_bp


@api_bp.route('/borrowers', methods=['GET'])
def get_borrowers():
    """
    Get paginated list of borrowers with optional filters.

    Query parameters:
        - verificationStatus: Filter by verification status
        - riskTier: Filter by risk tier
        - department: Filter by department
        - search: Search by name or DPI
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


@api_bp.route('/borrowers', methods=['POST'])
def create_borrower():
    """
    Create a new borrower.
    """
    return jsonify({
        "message": "Create borrower endpoint - implementation pending"
    }), 501


@api_bp.route('/borrowers/<borrower_id>', methods=['GET'])
def get_borrower(borrower_id):
    """
    Get borrower details by ID.
    """
    return jsonify({
        "message": f"Get borrower {borrower_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/borrowers/<borrower_id>', methods=['PUT'])
def update_borrower(borrower_id):
    """
    Update borrower details.
    """
    return jsonify({
        "message": f"Update borrower {borrower_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/borrowers/<borrower_id>/verify', methods=['POST'])
def verify_borrower(borrower_id):
    """
    Verify a borrower.
    """
    return jsonify({
        "message": f"Verify borrower {borrower_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/borrowers/<borrower_id>/loans', methods=['GET'])
def get_borrower_loans(borrower_id):
    """
    Get all loans for a borrower.
    """
    return jsonify({
        "message": f"Get borrower {borrower_id} loans endpoint - implementation pending"
    }), 501
