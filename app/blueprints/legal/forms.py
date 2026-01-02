from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from ...models.document import DocumentType


class DocumentUploadForm(FlaskForm):
    document_type = SelectField('Document Type', validators=[DataRequired()],
                               choices=[
                                   (DocumentType.MUTUO_MERCANTIL.value, 'Mutuo Mercantil'),
                                   (DocumentType.PAGARE.value, 'Pagaré'),
                                   (DocumentType.PROMESA_COMPRAVENTA.value, 'Promesa de Compraventa'),
                                   (DocumentType.ANNEX.value, 'Annex'),
                                   (DocumentType.DPI_COPY.value, 'DPI Copy'),
                                   (DocumentType.PROOF_OF_INCOME.value, 'Proof of Income'),
                                   (DocumentType.PROPERTY_TITLE.value, 'Property Title'),
                                   (DocumentType.APPRAISAL.value, 'Appraisal'),
                                   (DocumentType.OTHER.value, 'Other'),
                               ])
    name = StringField('Document Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    file = FileField('Document (PDF)', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDF files only')
    ])
    submit = SubmitField('Upload Document')


class DocumentAcceptanceForm(FlaskForm):
    submit = SubmitField('Accept and Sign Document')
