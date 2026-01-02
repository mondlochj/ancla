from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from ...utils.helpers import get_department_choices


class PropertyForm(FlaskForm):
    property_type = SelectField('Property Type', choices=[
        ('Land', 'Land'),
        ('House', 'House'),
        ('Commercial', 'Commercial'),
        ('Agricultural', 'Agricultural')
    ], validators=[DataRequired()])

    finca = StringField('Finca', validators=[DataRequired()])
    folio = StringField('Folio', validators=[DataRequired()])
    libro = StringField('Libro', validators=[DataRequired()])

    department = SelectField('Department', validators=[DataRequired()])
    municipality = StringField('Municipality', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[Optional()])

    latitude = DecimalField('Latitude', validators=[Optional()], places=6)
    longitude = DecimalField('Longitude', validators=[Optional()], places=6)

    market_value = DecimalField('Market Value (Q)', validators=[
        DataRequired(),
        NumberRange(min=1, message='Market value must be positive')
    ], places=2)

    appraised_value = DecimalField('Appraised Value (Q)', validators=[Optional()], places=2)
    appraisal_date = DateField('Appraisal Date', validators=[Optional()])
    appraised_by = StringField('Appraised By', validators=[Optional()])

    title_pdf = FileField('Title Document (PDF)', validators=[
        FileAllowed(['pdf'], 'PDF files only')
    ])

    submit = SubmitField('Save Property')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department.choices = [('', 'Select...')] + get_department_choices()


class PropertyPhotoForm(FlaskForm):
    photo = FileField('Photo', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only')
    ])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Upload Photo')


class PropertyVerificationForm(FlaskForm):
    verification_notes = TextAreaField('Verification Notes', validators=[Optional()])
    submit = SubmitField('Verify Property')
