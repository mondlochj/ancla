# Ancla Capital

A lending management platform for Ancla Capital, S.A. - a private lending company based in Guatemala.

## Features

### Loan Management
- Create and track loan applications
- Multi-stage workflow: Draft → Under Review → Approved → Active → Matured/Closed
- Automatic payment schedule generation
- LTV (Loan-to-Value) calculation
- Support for different loan products

### Borrower Management
- Borrower profiles with DPI verification
- Document upload and management
- Borrower portal for viewing loan status and payment history

### Collateral Management
- Property registration with market valuations
- Property verification workflow
- Support for multiple properties per borrower

### Payment Processing
- Record payments (regular, interest-only, principal-only, late fees)
- Automatic payment allocation to scheduled installments
- Overdue payment tracking
- Payment history and receipts

### Collections
- Automatic identification of delinquent loans
- Collection action tracking (calls, visits, notices)
- Legal readiness workflow for defaulted loans

### Email Notifications
- Embedded company logo in all emails
- Automatic notifications for:
  - Loan approval
  - Loan activation/disbursement
  - Payment received confirmation
  - Payment reminders (configurable days before due)
  - Overdue notices

### Reporting & Audit
- Dashboard with portfolio overview
- Loan and payment reports
- Complete audit trail of all actions

## Tech Stack

- **Backend:** Python 3.10+, Flask
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Authentication:** Flask-Login with role-based access control
- **Email:** SMTP with TLS support
- **Server:** Gunicorn + Apache (reverse proxy)

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL
- SMTP server for email

### Setup

1. Clone the repository:
```bash
git clone git@github.com:mondlochj/ancla.git
cd ancla
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Initialize database:
```bash
flask db upgrade
flask create-admin  # Create initial admin user
```

6. Run development server:
```bash
flask run
```

## Configuration

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/ancla

# Security
SECRET_KEY=your-secret-key

# Email
SMTP_SERVER=mail.example.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=noreply@example.com
SMTP_PASSWORD=your-password
FROM_EMAIL=noreply@example.com

# Server (production)
SERVER_NAME=example.com
```

## CLI Commands

### Payment Reminders
Send payment reminders for upcoming due payments:
```bash
flask send-payment-reminders --days-before 3
```

### Overdue Notices
Send overdue notices for missed payments:
```bash
flask send-overdue-notices
```

### Scheduled Tasks (Cron)
```bash
# Daily at 8:00 AM - Payment reminders
0 8 * * * cd /opt/ancla && FLASK_APP=run.py flask send-payment-reminders --days-before 3

# Daily at 9:00 AM - Overdue notices
0 9 * * * cd /opt/ancla && FLASK_APP=run.py flask send-overdue-notices
```

## User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management |
| **CreditOfficer** | Create/approve loans, manage borrowers |
| **Collections** | View overdue loans, record collection actions |
| **Legal** | Manage legal documents for defaulted loans |
| **Borrower** | View own loans, upload documents |

## Project Structure

```
ancla/
├── app/
│   ├── blueprints/          # Route handlers
│   │   ├── admin/           # Admin dashboard, reports
│   │   ├── auth/            # Login, registration
│   │   ├── borrowers/       # Borrower management
│   │   ├── collateral/      # Property management
│   │   ├── collections/     # Collections workflow
│   │   ├── legal/           # Legal documents
│   │   ├── loans/           # Loan management
│   │   └── payments/        # Payment processing
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   │   ├── email.py         # Email notifications
│   │   ├── loan_service.py  # Loan operations
│   │   └── payment_service.py
│   ├── templates/           # Jinja2 templates
│   ├── static/              # CSS, images
│   └── utils/               # Helpers, decorators
├── uploads/                 # User uploaded documents
├── logs/                    # Application logs
├── run.py                   # Application entry point
└── requirements.txt
```

## Business Rules

- **Minimum Loan Amount:** Q10,000
- **Maximum LTV:** 40%
- **Default Interest Rate:** 10% monthly
- **Late Fee Rate:** 5%
- **Grace Period:** 5 days
- **Legal Ready:** After 30 days overdue

## License

Proprietary - Ancla Capital, S.A.

## Contact

Ancla Capital, S.A. - Guatemala
