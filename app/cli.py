"""Flask CLI commands for scheduled tasks."""
import click
from datetime import date, timedelta
from flask import current_app
from flask.cli import with_appcontext

from .extensions import db
from .models.loan import Loan, LoanStatus
from .models.payment import PaymentSchedule
from .services.email import send_loan_notification


@click.command('send-payment-reminders')
@click.option('--days-before', default=3, help='Days before due date to send reminder')
@with_appcontext
def send_payment_reminders(days_before):
    """Send payment reminder emails for upcoming due payments."""
    target_date = date.today() + timedelta(days=days_before)

    # Find unpaid payments due on target date
    upcoming_payments = db.session.query(
        PaymentSchedule, Loan
    ).join(Loan).filter(
        PaymentSchedule.is_paid == False,
        PaymentSchedule.due_date == target_date,
        Loan.status == LoanStatus.ACTIVE.value
    ).all()

    sent_count = 0
    error_count = 0

    for schedule, loan in upcoming_payments:
        if loan.borrower.email:
            try:
                result = send_loan_notification(
                    loan.borrower, loan, 'payment_reminder',
                    extra_info={
                        'payment_amount': schedule.total_due,
                        'due_date': schedule.due_date
                    }
                )
                if result:
                    sent_count += 1
                    click.echo(f'Sent reminder to {loan.borrower.email} for loan {loan.loan_number}')
                else:
                    error_count += 1
                    click.echo(f'Failed to send reminder to {loan.borrower.email}', err=True)
            except Exception as e:
                error_count += 1
                click.echo(f'Error sending to {loan.borrower.email}: {str(e)}', err=True)

    click.echo(f'\nPayment reminders sent: {sent_count}, errors: {error_count}')


@click.command('send-overdue-notices')
@with_appcontext
def send_overdue_notices():
    """Send overdue payment notices for loans with missed payments."""
    today = date.today()

    # Find overdue payments
    overdue_payments = db.session.query(
        PaymentSchedule, Loan
    ).join(Loan).filter(
        PaymentSchedule.is_paid == False,
        PaymentSchedule.due_date < today,
        Loan.status.in_([LoanStatus.ACTIVE.value, LoanStatus.MATURED.value, LoanStatus.DEFAULTED.value])
    ).order_by(PaymentSchedule.due_date).all()

    # Group by loan to send one email per loan
    loans_notified = set()
    sent_count = 0
    error_count = 0

    for schedule, loan in overdue_payments:
        if loan.id in loans_notified:
            continue

        if loan.borrower.email:
            days_overdue = (today - schedule.due_date).days
            try:
                result = send_loan_notification(
                    loan.borrower, loan, 'overdue',
                    extra_info={
                        'payment_amount': schedule.total_due,
                        'due_date': schedule.due_date,
                        'days_overdue': days_overdue
                    }
                )
                if result:
                    sent_count += 1
                    loans_notified.add(loan.id)
                    click.echo(f'Sent overdue notice to {loan.borrower.email} for loan {loan.loan_number} ({days_overdue} days overdue)')
                else:
                    error_count += 1
                    click.echo(f'Failed to send overdue notice to {loan.borrower.email}', err=True)
            except Exception as e:
                error_count += 1
                click.echo(f'Error sending to {loan.borrower.email}: {str(e)}', err=True)

    click.echo(f'\nOverdue notices sent: {sent_count}, errors: {error_count}')


def register_cli_commands(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(send_payment_reminders)
    app.cli.add_command(send_overdue_notices)
