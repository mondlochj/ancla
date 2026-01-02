from datetime import date
from dateutil.relativedelta import relativedelta
from ..models.loan import Loan, LoanStatus, LoanProduct
from ..models.payment import PaymentSchedule
from ..extensions import db


class LoanValidationError(Exception):
    pass


def validate_loan_for_approval(loan):
    """Validate all mandatory gates before loan approval."""
    errors = []

    if loan.status != LoanStatus.UNDER_REVIEW.value:
        errors.append('Loan must be under review to approve')

    if not loan.borrower.is_verified:
        errors.append('Borrower must be verified')

    if not loan.collateral.verified:
        errors.append('Property must be verified by Legal')

    if loan.collateral.has_active_loan():
        # Check if it's not this loan
        for active_loan in loan.collateral.loans:
            if active_loan.id != loan.id and active_loan.status in [
                LoanStatus.ACTIVE.value,
                LoanStatus.APPROVED.value
            ]:
                errors.append('Property already has an active loan')
                break

    if loan.ltv > loan.product.max_ltv:
        errors.append(f'LTV ({loan.ltv*100:.1f}%) exceeds maximum ({loan.product.max_ltv*100:.1f}%)')

    if loan.loan_amount < loan.product.min_amount:
        errors.append(f'Loan amount below minimum ({loan.product.min_amount})')

    if loan.loan_amount > loan.product.max_amount:
        errors.append(f'Loan amount exceeds maximum ({loan.product.max_amount})')

    return errors


def validate_loan_for_activation(loan):
    """Validate loan before activation/disbursement."""
    errors = []

    if loan.status != LoanStatus.APPROVED.value:
        errors.append('Loan must be approved before activation')

    if not loan.all_documents_complete():
        errors.append('All legal documents must be executed')

    return errors


def approve_loan(loan, approver, notes=None):
    """Approve a loan after validation."""
    errors = validate_loan_for_approval(loan)
    if errors:
        raise LoanValidationError('; '.join(errors))

    loan.status = LoanStatus.APPROVED.value
    loan.approved_by = approver.id
    loan.approved_at = db.func.now()
    loan.approval_notes = notes

    return loan


def activate_loan(loan, notes=None):
    """Activate a loan and generate payment schedule."""
    errors = validate_loan_for_activation(loan)
    if errors:
        raise LoanValidationError('; '.join(errors))

    loan.status = LoanStatus.ACTIVE.value
    loan.disbursement_date = date.today()
    loan.maturity_date = loan.calculate_maturity_date(date.today())

    generate_payment_schedule(loan)

    return loan


def generate_payment_schedule(loan):
    """Generate interest-only payment schedule with balloon principal."""
    # Delete any existing schedule
    PaymentSchedule.query.filter_by(loan_id=loan.id).delete()

    start_date = loan.disbursement_date or date.today()
    monthly_interest = loan.loan_amount * loan.interest_rate

    for i in range(loan.term_months):
        payment_number = i + 1
        due_date = start_date + relativedelta(months=payment_number)

        # Last payment includes principal (balloon)
        if payment_number == loan.term_months:
            principal_due = loan.loan_amount
        else:
            principal_due = 0

        schedule_item = PaymentSchedule(
            loan_id=loan.id,
            payment_number=payment_number,
            due_date=due_date,
            principal_due=principal_due,
            interest_due=monthly_interest
        )
        db.session.add(schedule_item)

    db.session.commit()
    return loan.schedule.all()


def check_loan_default(loan, default_days=15, legal_ready_days=30):
    """Check and update loan status based on days past due."""
    days_overdue = loan.days_past_due

    if days_overdue >= legal_ready_days and loan.status == LoanStatus.DEFAULTED.value:
        loan.status = LoanStatus.LEGAL_READY.value
    elif days_overdue >= default_days and loan.status == LoanStatus.ACTIVE.value:
        loan.status = LoanStatus.DEFAULTED.value

    return loan


def calculate_loan_ltv(loan_amount, property_value):
    """Calculate Loan-to-Value ratio."""
    if not property_value or property_value == 0:
        return 0
    return float(loan_amount) / float(property_value)


def get_loan_summary(loan):
    """Get comprehensive loan summary."""
    total_paid_interest = sum(
        p.amount for p in loan.payments
        if p.payment_type == 'Interest'
    )
    total_paid_principal = sum(
        p.amount for p in loan.payments
        if p.payment_type == 'Principal'
    )
    total_paid_fees = sum(
        p.amount for p in loan.payments
        if p.payment_type == 'LateFee'
    )

    return {
        'loan_amount': loan.loan_amount,
        'total_interest': loan.total_interest,
        'total_repayment': loan.total_repayment,
        'paid_interest': total_paid_interest,
        'paid_principal': total_paid_principal,
        'paid_fees': total_paid_fees,
        'outstanding_principal': loan.outstanding_principal,
        'outstanding_interest': loan.outstanding_interest,
        'days_past_due': loan.days_past_due
    }
