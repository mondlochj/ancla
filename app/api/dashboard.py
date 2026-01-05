"""
Dashboard API endpoints.

Provides portfolio metrics and analytics for the dashboard.
"""

from flask import jsonify
from . import api_bp


@api_bp.route('/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """
    Get dashboard metrics including portfolio value, loan counts, and default rates.

    Response:
        {
            "totalPortfolioValue": 2500000,
            "activeLoansCount": 45,
            "defaultRate": 0.033,
            "averageLtv": 0.32,
            "monthlyInterestIncome": 250000,
            "overduePaymentsCount": 3,
            "overdueAmount": 45000,
            "loansByStatus": { ... },
            "loansByDepartment": { ... }
        }
    """
    # TODO: Implement with actual database queries
    return jsonify({
        "totalPortfolioValue": 2500000,
        "activeLoansCount": 45,
        "defaultRate": 0.033,
        "averageLtv": 0.32,
        "monthlyInterestIncome": 250000,
        "overduePaymentsCount": 3,
        "overdueAmount": 45000,
        "loansByStatus": {
            "Draft": 2,
            "UnderReview": 5,
            "Approved": 3,
            "Active": 45,
            "Matured": 12,
            "Defaulted": 2,
            "LegalReady": 1,
            "Closed": 20
        },
        "loansByDepartment": {
            "Guatemala": 25,
            "Escuintla": 10,
            "Sacatepéquez": 8,
            "Quetzaltenango": 7
        }
    }), 200


@api_bp.route('/dashboard/portfolio', methods=['GET'])
def get_portfolio_summary():
    """
    Get detailed portfolio summary with trends.
    """
    return jsonify({
        "message": "Portfolio summary endpoint - implementation pending"
    }), 501
