from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, DateField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from ...models.payment import PaymentType


class PaymentForm(FlaskForm):
    amount = DecimalField('Amount (Q)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Amount must be positive')
    ], places=2)
    payment_type = SelectField('Payment Type', validators=[DataRequired()],
                              choices=[
                                  (PaymentType.INTEREST.value, 'Interest'),
                                  (PaymentType.PRINCIPAL.value, 'Principal'),
                                  (PaymentType.LATE_FEE.value, 'Late Fee'),
                                  (PaymentType.OTHER.value, 'Other'),
                              ])
    payment_date = DateField('Payment Date', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('Cash', 'Cash'),
        ('Transfer', 'Bank Transfer'),
        ('Check', 'Check'),
        ('Other', 'Other')
    ])
    reference_number = StringField('Reference Number', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Payment')
