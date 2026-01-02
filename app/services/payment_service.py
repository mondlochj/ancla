from datetime import date
from decimal import Decimal
from ..models.payment import Payment, PaymentSchedule, PaymentType
from ..models.loan import Loan, LoanStatus
from ..extensions import db


def record_payment(loan, amount, payment_type, payment_date, recorded_by,
                  payment_method=None, reference_number=None, notes=None):
    """Record a payment against a loan."""
    payment = Payment(
        loan_id=loan.id,
        amount=amount,
        payment_type=payment_type,
        payment_date=payment_date,
        payment_method=payment_method,
        reference_number=reference_number,
        notes=notes,
        recorded_by=recorded_by
    )

    db.session.add(payment)

    # Auto-apply to schedule if interest payment
    if payment_type == PaymentType.INTEREST.value:
        apply_payment_to_schedule(loan, amount, payment_date)

    # Check if loan is fully paid
    check_loan_payoff(loan)

    return payment


def apply_payment_to_schedule(loan, amount, payment_date):
    """Apply an interest payment to the payment schedule."""
    remaining = Decimal(str(amount))

    # Find unpaid schedule items
    unpaid_items = loan.schedule.filter_by(is_paid=False).order_by(
        PaymentSchedule.due_date
    ).all()

    for item in unpaid_items:
        if remaining <= 0:
            break

        item_total = item.interest_due + item.late_fee
        if remaining >= item_total:
            item.mark_paid(payment_date)
            remaining -= item_total
        # Partial payments don't mark as paid


def calculate_late_fees(loan):
    """Calculate and apply late fees to overdue schedule items."""
    late_fee_rate = loan.product.late_fee_rate

    overdue_items = loan.schedule.filter(
        PaymentSchedule.is_paid == False,
        PaymentSchedule.due_date < date.today(),
        PaymentSchedule.late_fee == 0
    ).all()

    total_fees = Decimal('0')
    for item in overdue_items:
        fee = item.calculate_late_fee(late_fee_rate)
        total_fees += fee

    return total_fees


def check_loan_payoff(loan):
    """Check if loan is fully paid and update status."""
    # Check if all schedule items are paid
    unpaid = loan.schedule.filter_by(is_paid=False).count()

    if unpaid == 0:
        loan.status = LoanStatus.CLOSED.value


def get_loan_payment_summary(loan):
    """Get detailed payment summary for a loan."""
    payments = loan.payments.all()

    summary = {
        'total_interest_paid': Decimal('0'),
        'total_principal_paid': Decimal('0'),
        'total_fees_paid': Decimal('0'),
        'total_other_paid': Decimal('0'),
        'payment_count': len(payments),
        'last_payment_date': None
    }

    for p in payments:
        if p.payment_type == PaymentType.INTEREST.value:
            summary['total_interest_paid'] += p.amount
        elif p.payment_type == PaymentType.PRINCIPAL.value:
            summary['total_principal_paid'] += p.amount
        elif p.payment_type == PaymentType.LATE_FEE.value:
            summary['total_fees_paid'] += p.amount
        else:
            summary['total_other_paid'] += p.amount

        if summary['last_payment_date'] is None or p.payment_date > summary['last_payment_date']:
            summary['last_payment_date'] = p.payment_date

    summary['total_paid'] = (
        summary['total_interest_paid'] +
        summary['total_principal_paid'] +
        summary['total_fees_paid'] +
        summary['total_other_paid']
    )

    return summary


def get_overdue_loans():
    """Get all loans with overdue payments."""
    today = date.today()

    overdue_schedules = PaymentSchedule.query.filter(
        PaymentSchedule.is_paid == False,
        PaymentSchedule.due_date < today
    ).all()

    loan_ids = set(s.loan_id for s in overdue_schedules)
    return Loan.query.filter(
        Loan.id.in_(loan_ids),
        Loan.status == LoanStatus.ACTIVE.value
    ).all()
