import re
from wtforms.validators import ValidationError


class GuatemalaDPI:
    """Validator for Guatemala DPI (Documento Personal de Identificacion)."""

    def __init__(self, message=None):
        self.message = message or 'Invalid DPI format. Must be 13 digits.'

    def __call__(self, form, field):
        dpi = field.data
        if dpi:
            # Remove spaces and dashes
            dpi = re.sub(r'[\s-]', '', dpi)
            if not re.match(r'^\d{13}$', dpi):
                raise ValidationError(self.message)


class GuatemalaNIT:
    """Validator for Guatemala NIT (Numero de Identificacion Tributaria)."""

    def __init__(self, message=None):
        self.message = message or 'Invalid NIT format.'

    def __call__(self, form, field):
        nit = field.data
        if nit:
            # Remove spaces, dashes and check digit suffix
            nit = re.sub(r'[\s-]', '', nit)
            # NIT can be 8-9 digits plus optional check digit (K or digit)
            if not re.match(r'^\d{7,9}[0-9K]?$', nit, re.IGNORECASE):
                raise ValidationError(self.message)


class GuatemalaPhone:
    """Validator for Guatemala phone numbers."""

    def __init__(self, message=None):
        self.message = message or 'Invalid phone number. Use 8 digits for Guatemala.'

    def __call__(self, form, field):
        phone = field.data
        if phone:
            # Remove common formatting
            phone = re.sub(r'[\s\-\(\)\+]', '', phone)
            # Accept 8 digits (local) or with country code (502)
            if not re.match(r'^(502)?\d{8}$', phone):
                raise ValidationError(self.message)


class PositiveDecimal:
    """Validator for positive decimal numbers."""

    def __init__(self, message=None):
        self.message = message or 'Value must be a positive number.'

    def __call__(self, form, field):
        if field.data is not None and field.data <= 0:
            raise ValidationError(self.message)


class LTVValidator:
    """Validator for Loan-to-Value ratio."""

    def __init__(self, max_ltv=0.40, message=None):
        self.max_ltv = max_ltv
        self.message = message or f'LTV cannot exceed {max_ltv * 100}%.'

    def __call__(self, form, field):
        if field.data is not None and field.data > self.max_ltv:
            raise ValidationError(self.message)


def validate_registry_number(finca, folio, libro):
    """Validate property registry number format."""
    errors = []
    if not finca or not re.match(r'^\d+$', str(finca)):
        errors.append('Finca must be a number')
    if not folio or not re.match(r'^\d+$', str(folio)):
        errors.append('Folio must be a number')
    if not libro:
        errors.append('Libro is required')
    return errors


def format_currency(amount):
    """Format amount as Guatemalan Quetzal."""
    if amount is None:
        return 'Q0.00'
    return f'Q{amount:,.2f}'


def format_percentage(decimal_value):
    """Format decimal as percentage."""
    if decimal_value is None:
        return '0%'
    return f'{decimal_value * 100:.2f}%'
