"""
Loans API endpoints.

Provides CRUD operations for loans.
"""

from flask import request, jsonify
from . import api_bp


@api_bp.route('/loans', methods=['GET'])
def get_loans():
    """
    Get paginated list of loans with optional filters.

    Query parameters:
        - status: Filter by loan status
        - borrowerId: Filter by borrower
        - search: Search by reference number or borrower name
        - page: Page number (default: 1)
        - pageSize: Items per page (default: 20)

    Response:
        {
            "data": [ ... ],
            "total": 100,
            "page": 1,
            "pageSize": 20,
            "totalPages": 5
        }
    """
    # TODO: Implement with actual database queries
    return jsonify({
        "data": [],
        "total": 0,
        "page": 1,
        "pageSize": 20,
        "totalPages": 0
    }), 200


@api_bp.route('/loans', methods=['POST'])
def create_loan():
    """
    Create a new loan.

    Request body:
        {
            "borrowerId": "uuid",
            "propertyId": "uuid",
            "loanProductId": "uuid",
            "amount": 100000,
            "termMonths": 12,
            "interestRate": 0.10
        }
    """
    return jsonify({
        "message": "Create loan endpoint - implementation pending"
    }), 501


@api_bp.route('/loans/<loan_id>', methods=['GET'])
def get_loan(loan_id):
    """
    Get loan details by ID.
    """
    return jsonify({
        "message": f"Get loan {loan_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/loans/<loan_id>', methods=['PUT'])
def update_loan(loan_id):
    """
    Update loan details.
    """
    return jsonify({
        "message": f"Update loan {loan_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/loans/<loan_id>/approve', methods=['POST'])
def approve_loan(loan_id):
    """
    Approve a loan that is under review.

    Request body:
        {
            "notes": "Approval notes"
        }
    """
    return jsonify({
        "message": f"Approve loan {loan_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/loans/<loan_id>/activate', methods=['POST'])
def activate_loan(loan_id):
    """
    Activate/disburse an approved loan.
    """
    return jsonify({
        "message": f"Activate loan {loan_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/loans/<loan_id>/schedule', methods=['GET'])
def get_loan_schedule(loan_id):
    """
    Get payment schedule for a loan.
    """
    return jsonify({
        "message": f"Get loan {loan_id} schedule endpoint - implementation pending"
    }), 501


@api_bp.route('/loans/<loan_id>/payments', methods=['GET'])
def get_loan_payments(loan_id):
    """
    Get payment history for a loan.
    """
    return jsonify({
        "message": f"Get loan {loan_id} payments endpoint - implementation pending"
    }), 501
