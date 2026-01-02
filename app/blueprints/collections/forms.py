from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, StringField, IntegerField, DecimalField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from ...models.collection import ActionType


class CollectionActionForm(FlaskForm):
    action_type = SelectField('Action Type', validators=[DataRequired()],
                             choices=[
                                 (ActionType.PHONE_CALL.value, 'Phone Call'),
                                 (ActionType.SMS.value, 'SMS'),
                                 (ActionType.EMAIL.value, 'Email'),
                                 (ActionType.VISIT.value, 'Visit'),
                                 (ActionType.LETTER.value, 'Letter'),
                                 (ActionType.PAYMENT_PROMISE.value, 'Payment Promise'),
                                 (ActionType.LEGAL_NOTICE.value, 'Legal Notice'),
                                 (ActionType.NOTE.value, 'Note'),
                             ])
    notes = TextAreaField('Notes', validators=[DataRequired()])
    contact_name = StringField('Contact Name', validators=[Optional()])
    contact_phone = StringField('Contact Phone', validators=[Optional()])
    contact_result = StringField('Contact Result', validators=[Optional()])

    # Payment promise
    promise_amount = DecimalField('Promise Amount', validators=[Optional()], places=2)
    promise_date = DateField('Promise Date', validators=[Optional()])

    submit = SubmitField('Record Action')


class ExtensionForm(FlaskForm):
    extension_days = IntegerField('Extension Days', validators=[
        DataRequired(),
        NumberRange(min=1, max=30, message='Extension must be 1-30 days')
    ])
    notes = TextAreaField('Reason for Extension', validators=[DataRequired()])
    submit = SubmitField('Grant Extension')


class LegalEscalationForm(FlaskForm):
    notes = TextAreaField('Escalation Notes', validators=[DataRequired()])
    submit = SubmitField('Escalate to Legal')
