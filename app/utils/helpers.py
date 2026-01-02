import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app


ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_document(filename):
    """Check if file is an allowed document type."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENT_EXTENSIONS


def allowed_image(filename):
    """Check if file is an allowed image type."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def save_uploaded_file(file, subfolder='documents'):
    """Save an uploaded file and return the path."""
    if not file:
        return None

    filename = secure_filename(file.filename)
    # Add unique prefix to avoid collisions
    unique_filename = f'{uuid.uuid4().hex}_{filename}'

    upload_folder = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        subfolder
    )
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    # Return relative path from upload folder
    return os.path.join(subfolder, unique_filename)


def delete_uploaded_file(file_path):
    """Delete an uploaded file."""
    if not file_path:
        return

    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)
    if os.path.exists(full_path):
        os.remove(full_path)


def get_file_path(relative_path):
    """Get full file path from relative path."""
    if not relative_path:
        return None
    return os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)


# Guatemala departments
GUATEMALA_DEPARTMENTS = [
    'Alta Verapaz',
    'Baja Verapaz',
    'Chimaltenango',
    'Chiquimula',
    'El Progreso',
    'Escuintla',
    'Guatemala',
    'Huehuetenango',
    'Izabal',
    'Jalapa',
    'Jutiapa',
    'Peten',
    'Quetzaltenango',
    'Quiche',
    'Retalhuleu',
    'Sacatepequez',
    'San Marcos',
    'Santa Rosa',
    'Solola',
    'Suchitepequez',
    'Totonicapan',
    'Zacapa'
]


def get_department_choices():
    """Return list of department choices for forms."""
    return [(d, d) for d in GUATEMALA_DEPARTMENTS]


def format_date(date_obj, format_str='%d/%m/%Y'):
    """Format date for display."""
    if date_obj is None:
        return ''
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    return date_obj.strftime(format_str)


def mask_dpi(dpi):
    """Mask DPI for display, showing only last 4 digits."""
    if not dpi:
        return '****'
    return '*' * (len(dpi) - 4) + dpi[-4:]


def calculate_ltv(loan_amount, property_value):
    """Calculate Loan-to-Value ratio."""
    if not property_value or property_value == 0:
        return 0
    return float(loan_amount) / float(property_value)
