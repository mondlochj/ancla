from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional
from ...models.loan import LoanProduct


class LoanForm(FlaskForm):
    product_id = SelectField('Loan Product', coerce=int, validators=[DataRequired()])
    loan_amount = DecimalField('Loan Amount (Q)', validators=[
        DataRequired(),
        NumberRange(min=10000, message='Minimum loan amount is Q10,000')
    ], places=2)
    term_months = IntegerField('Term (Months)', validators=[
        DataRequired(),
        NumberRange(min=1, max=12, message='Term must be 1-12 months')
    ])
    interest_rate = DecimalField('Monthly Interest Rate', validators=[
        DataRequired(),
        NumberRange(min=0.01, max=0.20, message='Interest rate must be between 1% and 20%')
    ], places=4)

    submit = SubmitField('Create Loan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_id.choices = [
            (p.id, f'{p.name} ({p.interest_rate*100:.1f}% monthly)')
            for p in LoanProduct.query.filter_by(is_active=True).all()
        ]


class LoanApprovalForm(FlaskForm):
    approval_notes = TextAreaField('Approval Notes', validators=[Optional()])
    submit_approve = SubmitField('Approve Loan')
    submit_reject = SubmitField('Return to Draft')


class LoanActivationForm(FlaskForm):
    disbursement_notes = TextAreaField('Disbursement Notes', validators=[Optional()])
    submit = SubmitField('Activate Loan')


class LoanStatusForm(FlaskForm):
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Update Status')
