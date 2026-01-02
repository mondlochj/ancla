import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import current_app, url_for, render_template_string


def get_logo_path():
    """Get the path to the logo file."""
    return os.path.join(os.path.dirname(__file__), '..', 'static', 'logo.png')


def get_email_header():
    """Generate the common email header HTML with logo using CID reference."""
    return '''
        <div class="header" style="background: #1a365d; color: white; padding: 20px; text-align: center;">
            <table align="center" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td style="vertical-align: middle; padding-right: 15px;">
                        <img src="cid:logo" alt="Ancla Capital" style="height: 60px; display: block;">
                    </td>
                    <td style="vertical-align: middle;">
                        <h1 style="margin: 0; font-size: 24px; color: white;">Ancla Capital, S.A.</h1>
                    </td>
                </tr>
            </table>
        </div>
    '''


def send_email(to_email, subject, html_body, text_body=None):
    """Send an email using SMTP configuration with embedded logo."""
    config = current_app.config

    # Create the root message as 'related' to support embedded images
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = subject
    msg_root['From'] = config['FROM_EMAIL']
    msg_root['To'] = to_email

    # Create alternative part for text/html
    msg_alt = MIMEMultipart('alternative')
    msg_root.attach(msg_alt)

    if text_body:
        msg_alt.attach(MIMEText(text_body, 'plain'))
    msg_alt.attach(MIMEText(html_body, 'html'))

    # Attach logo image with Content-ID
    logo_path = get_logo_path()
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'rb') as f:
                logo_img = MIMEImage(f.read())
                logo_img.add_header('Content-ID', '<logo>')
                logo_img.add_header('Content-Disposition', 'inline', filename='logo.png')
                msg_root.attach(logo_img)
        except Exception as e:
            current_app.logger.warning(f'Could not attach logo: {str(e)}')

    try:
        server = smtplib.SMTP(config['SMTP_SERVER'], config['SMTP_PORT'])
        if config['SMTP_USE_TLS']:
            server.starttls()
        server.login(config['SMTP_USERNAME'], config['SMTP_PASSWORD'])
        server.sendmail(config['FROM_EMAIL'], to_email, msg_root.as_string())
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f'Email send failed: {str(e)}')
        return False


def send_verification_email(user):
    """Send email verification link to new user."""
    token = user.generate_verification_token()

    verification_url = url_for('auth.verify_email', token=token, _external=True)

    subject = 'Ancla Capital - Verify Your Email'

    email_header = get_email_header()
    html_body = render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .content { padding: 30px; background: #f9f9f9; }
        .button { display: inline-block; padding: 12px 30px; background: #2563eb;
                  color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        {{ email_header|safe }}
        <div class="content">
            <h2>Verify Your Email Address</h2>
            <p>Thank you for registering with Ancla Capital.</p>
            <p>Please click the button below to verify your email address:</p>
            <p style="text-align: center;">
                <a href="{{ verification_url }}" class="button">Verify Email</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all;">{{ verification_url }}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you did not create an account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Ancla Capital, S.A. - Guatemala</p>
            <p>This is an automated message. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
    ''', verification_url=verification_url, email_header=email_header)

    text_body = f'''
Ancla Capital, S.A.

Verify Your Email Address

Thank you for registering with Ancla Capital.

Please click the link below to verify your email address:
{verification_url}

This link will expire in 24 hours.

If you did not create an account, please ignore this email.

--
Ancla Capital, S.A. - Guatemala
    '''

    return send_email(user.email, subject, html_body, text_body)


def send_password_reset_email(user, reset_url):
    """Send password reset link."""
    subject = 'Ancla Capital - Password Reset'

    email_header = get_email_header()
    html_body = render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .content { padding: 30px; background: #f9f9f9; }
        .button { display: inline-block; padding: 12px 30px; background: #2563eb;
                  color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        {{ email_header|safe }}
        <div class="content">
            <h2>Password Reset Request</h2>
            <p>We received a request to reset your password.</p>
            <p>Click the button below to set a new password:</p>
            <p style="text-align: center;">
                <a href="{{ reset_url }}" class="button">Reset Password</a>
            </p>
            <p>This link will expire in 1 hour.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Ancla Capital, S.A. - Guatemala</p>
        </div>
    </div>
</body>
</html>
    ''', reset_url=reset_url, email_header=email_header)

    return send_email(user.email, subject, html_body)


def send_loan_notification(borrower, loan, notification_type, extra_info=None):
    """Send loan-related notifications to borrower.

    Args:
        borrower: The borrower object
        loan: The loan object
        notification_type: Type of notification (approved, activated, payment_reminder, payment_received, overdue)
        extra_info: Optional dict with additional info (e.g., payment amount, due date)
    """
    subject_map = {
        'approved': 'Ancla Capital - Your Loan Has Been Approved',
        'activated': 'Ancla Capital - Loan Disbursement Confirmation',
        'payment_reminder': 'Ancla Capital - Payment Reminder',
        'payment_received': 'Ancla Capital - Payment Received',
        'overdue': 'Ancla Capital - Payment Overdue Notice'
    }

    subject = subject_map.get(notification_type, 'Ancla Capital - Loan Notification')
    extra_info = extra_info or {}

    email_header = get_email_header()
    # Template selection based on notification type
    html_body = render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .content { padding: 30px; background: #f9f9f9; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .loan-info { background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        {{ email_header|safe }}
        <div class="content">
            <h2>{{ title }}</h2>
            <p>Dear {{ borrower.full_name }},</p>
            <p>{{ message }}</p>
            <div class="loan-info">
                <p><strong>Loan Number:</strong> {{ loan.loan_number }}</p>
                <p><strong>Amount:</strong> Q{{ "{:,.2f}".format(loan.loan_amount) }}</p>
                {% if extra_info.get('payment_amount') %}
                <p><strong>Payment Amount:</strong> Q{{ "{:,.2f}".format(extra_info.payment_amount) }}</p>
                {% endif %}
                {% if extra_info.get('due_date') %}
                <p><strong>Due Date:</strong> {{ extra_info.due_date.strftime('%d/%m/%Y') }}</p>
                {% endif %}
                {% if extra_info.get('days_overdue') %}
                <p><strong>Days Overdue:</strong> {{ extra_info.days_overdue }}</p>
                {% endif %}
            </div>
        </div>
        <div class="footer">
            <p>Ancla Capital, S.A. - Guatemala</p>
        </div>
    </div>
</body>
</html>
    ''', borrower=borrower, loan=loan, extra_info=extra_info,
       title=subject.replace('Ancla Capital - ', ''),
       message=_get_notification_message(notification_type),
       email_header=email_header)

    return send_email(borrower.email, subject, html_body)


def _get_notification_message(notification_type):
    messages = {
        'approved': 'Your loan application has been approved. Our team will contact you shortly regarding disbursement.',
        'activated': 'Your loan has been disbursed. Please review the payment schedule in your account.',
        'payment_reminder': 'This is a friendly reminder that your loan payment is due soon.',
        'payment_received': 'We have received your payment. Thank you for your timely payment.',
        'overdue': 'Your loan payment is overdue. Please make payment as soon as possible to avoid additional fees.'
    }
    return messages.get(notification_type, '')


def send_registration_invite(email, borrower_name):
    """Send invitation email to borrower to register for portal access."""
    register_url = url_for('auth.register', _external=True)

    subject = 'Ancla Capital - You Have Been Added as a Borrower'

    email_header = get_email_header()
    html_body = render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .content { padding: 30px; background: #f9f9f9; }
        .button { display: inline-block; padding: 12px 30px; background: #2563eb;
                  color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .highlight { background: #e0f2fe; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        {{ email_header|safe }}
        <div class="content">
            <h2>Welcome to Ancla Capital</h2>
            <p>Dear {{ borrower_name }},</p>
            <p>You have been added as a borrower in our lending platform. To access your account and view your loan information, please register using the link below:</p>
            <p style="text-align: center;">
                <a href="{{ register_url }}" class="button">Register Now</a>
            </p>
            <div class="highlight">
                <p><strong>Important:</strong> Please register using this email address: <strong>{{ email }}</strong></p>
                <p>This will automatically link your account to your borrower profile.</p>
            </div>
            <p>Once registered, you'll be able to:</p>
            <ul>
                <li>View your loan details and status</li>
                <li>Upload required documents</li>
                <li>View your payment schedule</li>
                <li>Track your payment history</li>
            </ul>
            <p>If you have any questions, please contact our office.</p>
        </div>
        <div class="footer">
            <p>Ancla Capital, S.A. - Guatemala</p>
            <p>This is an automated message. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
    ''', borrower_name=borrower_name, email=email, register_url=register_url, email_header=email_header)

    text_body = f'''
Ancla Capital, S.A.

Welcome to Ancla Capital

Dear {borrower_name},

You have been added as a borrower in our lending platform. To access your account and view your loan information, please register at:

{register_url}

IMPORTANT: Please register using this email address: {email}
This will automatically link your account to your borrower profile.

Once registered, you'll be able to:
- View your loan details and status
- Upload required documents
- View your payment schedule
- Track your payment history

If you have any questions, please contact our office.

--
Ancla Capital, S.A. - Guatemala
    '''

    return send_email(email, subject, html_body, text_body)
