"""
Collections API endpoints.

Provides endpoints for collections workflow.
"""

from flask import request, jsonify
from . import api_bp


@api_bp.route('/collections/delinquent', methods=['GET'])
def get_delinquent_loans():
    """
    Get list of delinquent loans for collections.

    Query parameters:
        - stage: Filter by collection stage
        - daysOverdue: Minimum days overdue
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


@api_bp.route('/collections/<loan_id>', methods=['GET'])
def get_loan_collection_details(loan_id):
    """
    Get collection details for a loan.
    """
    return jsonify({
        "message": f"Get collection details for loan {loan_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/collections/<loan_id>/actions', methods=['GET'])
def get_collection_actions(loan_id):
    """
    Get collection action history for a loan.
    """
    return jsonify({
        "data": [],
        "total": 0
    }), 200


@api_bp.route('/collections/<loan_id>/action', methods=['POST'])
def create_collection_action(loan_id):
    """
    Record a collection action.

    Request body:
        {
            "actionType": "PhoneCall",
            "contactedPerson": "Juan Pérez",
            "contactPhone": "5555-5555",
            "outcome": "Promised to pay",
            "promiseAmount": 10000,
            "promiseDate": "2024-01-15",
            "notes": "Action notes"
        }
    """
    return jsonify({
        "message": f"Create collection action for loan {loan_id} endpoint - implementation pending"
    }), 501
