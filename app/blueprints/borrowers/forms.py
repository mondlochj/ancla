from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length
from ...utils.validators import GuatemalaDPI, GuatemalaNIT, GuatemalaPhone
from ...utils.helpers import get_department_choices


class BorrowerForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    dpi = StringField('DPI', validators=[
        DataRequired(),
        GuatemalaDPI()
    ])
    nit = StringField('NIT', validators=[
        Optional(),
        GuatemalaNIT()
    ])
    phone = StringField('Phone', validators=[
        DataRequired(),
        GuatemalaPhone()
    ])
    email = StringField('Email', validators=[
        Optional(),
        Email()
    ])
    address = TextAreaField('Address', validators=[Optional()])
    department = SelectField('Department', validators=[DataRequired()])
    municipality = StringField('Municipality', validators=[Optional()])

    employment_type = SelectField('Employment Type', choices=[
        ('', 'Select...'),
        ('Employee', 'Employee'),
        ('SelfEmployed', 'Self Employed'),
        ('Business', 'Business Owner'),
        ('Retired', 'Retired'),
        ('Other', 'Other')
    ])
    employer_name = StringField('Employer Name', validators=[Optional()])
    business_name = StringField('Business Name', validators=[Optional()])
    monthly_income = DecimalField('Monthly Income (Q)', validators=[Optional()], places=2)

    risk_tier = SelectField('Risk Tier', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ], default='Medium')

    submit = SubmitField('Save Borrower')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department.choices = [('', 'Select...')] + get_department_choices()


class BorrowerVerificationForm(FlaskForm):
    verification_notes = TextAreaField('Verification Notes', validators=[Optional()])
    submit_verify = SubmitField('Verify Borrower')
    submit_reject = SubmitField('Reject')


class LinkUserForm(FlaskForm):
    user_email = StringField('User Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Link User Account')
