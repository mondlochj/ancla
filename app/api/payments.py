"""
Payments API endpoints.

Provides CRUD operations for payments.
"""

from flask import request, jsonify
from . import api_bp


@api_bp.route('/payments', methods=['GET'])
def get_payments():
    """
    Get paginated list of payments with optional filters.

    Query parameters:
        - loanId: Filter by loan
        - paymentType: Filter by payment type
        - startDate: Filter by start date
        - endDate: Filter by end date
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


@api_bp.route('/payments', methods=['POST'])
def create_payment():
    """
    Record a new payment.

    Request body:
        {
            "loanId": "uuid",
            "scheduleId": "uuid",  // optional
            "amount": 10000,
            "paymentType": "Principal",
            "paymentMethod": "Cash",
            "referenceNumber": "ABC123",
            "notes": "Payment notes"
        }
    """
    return jsonify({
        "message": "Create payment endpoint - implementation pending"
    }), 501


@api_bp.route('/payments/<payment_id>', methods=['GET'])
def get_payment(payment_id):
    """
    Get payment details by ID.
    """
    return jsonify({
        "message": f"Get payment {payment_id} endpoint - implementation pending"
    }), 501


@api_bp.route('/payments/overdue', methods=['GET'])
def get_overdue_payments():
    """
    Get list of overdue payments.
    """
    return jsonify({
        "data": [],
        "total": 0
    }), 200
