"""
Marshmallow schemas for API serialization.
"""

from marshmallow import Schema, fields, post_load, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import User, Role, Loan, LoanProduct, Borrower, Property, Payment, PaymentSchedule, Document, CollectionAction


class RoleSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    permissions = fields.Dict()


class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    email = fields.Email()
    fullName = fields.String(attribute='full_name')
    role = fields.Nested(RoleSchema)
    isVerified = fields.Boolean(attribute='is_verified')
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    lastLogin = fields.DateTime(attribute='last_login', dump_only=True)


class BorrowerSchema(Schema):
    id = fields.UUID(dump_only=True)
    dpi = fields.String()
    firstName = fields.String(attribute='first_name')
    lastName = fields.String(attribute='last_name')
    fullName = fields.String(attribute='full_name', dump_only=True)
    email = fields.Email(allow_none=True)
    phone = fields.String()
    alternatePhone = fields.String(attribute='alternate_phone', allow_none=True)
    address = fields.String()
    municipality = fields.String()
    department = fields.String()
    occupation = fields.String(allow_none=True)
    employer = fields.String(allow_none=True)
    monthlyIncome = fields.Float(attribute='monthly_income', allow_none=True)
    riskTier = fields.String(attribute='risk_tier')
    verificationStatus = fields.String(attribute='verification_status')
    verifiedBy = fields.Nested(UserSchema, attribute='verified_by', dump_only=True)
    verifiedAt = fields.DateTime(attribute='verified_at', dump_only=True)
    notes = fields.String(allow_none=True)
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)


class BorrowerCreateSchema(Schema):
    dpi = fields.String(required=True)
    firstName = fields.String(required=True, data_key='first_name')
    lastName = fields.String(required=True, data_key='last_name')
    email = fields.Email(allow_none=True)
    phone = fields.String(required=True)
    alternatePhone = fields.String(data_key='alternate_phone', allow_none=True)
    address = fields.String(required=True)
    municipality = fields.String(required=True)
    department = fields.String(required=True)
    occupation = fields.String(allow_none=True)
    employer = fields.String(allow_none=True)
    monthlyIncome = fields.Float(data_key='monthly_income', allow_none=True)
    riskTier = fields.String(data_key='risk_tier', load_default='Medium')
    notes = fields.String(allow_none=True)


class PropertySchema(Schema):
    id = fields.UUID(dump_only=True)
    finca = fields.String()
    folio = fields.String()
    libro = fields.String()
    address = fields.String()
    municipality = fields.String()
    department = fields.String()
    areaM2 = fields.Float(attribute='area_m2')
    marketValue = fields.Float(attribute='market_value')
    appraisalValue = fields.Float(attribute='appraisal_value', allow_none=True)
    appraisalDate = fields.Date(attribute='appraisal_date', allow_none=True)
    verificationStatus = fields.String(attribute='verification_status')
    verifiedBy = fields.Nested(UserSchema, attribute='verified_by', dump_only=True)
    verifiedAt = fields.DateTime(attribute='verified_at', dump_only=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    notes = fields.String(allow_none=True)
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)


class PropertyCreateSchema(Schema):
    finca = fields.String(required=True)
    folio = fields.String(required=True)
    libro = fields.String(required=True)
    address = fields.String(required=True)
    municipality = fields.String(required=True)
    department = fields.String(required=True)
    areaM2 = fields.Float(required=True, data_key='area_m2')
    marketValue = fields.Float(required=True, data_key='market_value')
    appraisalValue = fields.Float(data_key='appraisal_value', allow_none=True)
    appraisalDate = fields.Date(data_key='appraisal_date', allow_none=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    notes = fields.String(allow_none=True)


class LoanProductSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String()
    description = fields.String(allow_none=True)
    minAmount = fields.Float(attribute='min_amount')
    maxAmount = fields.Float(attribute='max_amount')
    minTermMonths = fields.Integer(attribute='min_term_months')
    maxTermMonths = fields.Integer(attribute='max_term_months')
    defaultInterestRate = fields.Float(attribute='default_interest_rate')
    isActive = fields.Boolean(attribute='is_active')


class LoanSchema(Schema):
    id = fields.UUID(dump_only=True)
    referenceNumber = fields.String(attribute='reference_number', dump_only=True)
    borrower = fields.Nested(BorrowerSchema)
    property = fields.Nested(PropertySchema)
    loanProduct = fields.Nested(LoanProductSchema, attribute='loan_product')
    amount = fields.Float()
    termMonths = fields.Integer(attribute='term_months')
    interestRate = fields.Float(attribute='interest_rate')
    ltv = fields.Float()
    status = fields.String()
    approvedBy = fields.Nested(UserSchema, attribute='approved_by', dump_only=True)
    approvedAt = fields.DateTime(attribute='approved_at', dump_only=True)
    activatedAt = fields.DateTime(attribute='activated_at', dump_only=True)
    maturityDate = fields.Date(attribute='maturity_date', dump_only=True)
    notes = fields.String(allow_none=True)
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)


class LoanCreateSchema(Schema):
    borrowerId = fields.UUID(required=True, data_key='borrower_id')
    propertyId = fields.UUID(required=True, data_key='property_id')
    loanProductId = fields.UUID(required=True, data_key='loan_product_id')
    amount = fields.Float(required=True)
    termMonths = fields.Integer(required=True, data_key='term_months')
    interestRate = fields.Float(required=True, data_key='interest_rate')
    notes = fields.String(allow_none=True)


class PaymentScheduleSchema(Schema):
    id = fields.UUID(dump_only=True)
    loanId = fields.UUID(attribute='loan_id')
    dueDate = fields.Date(attribute='due_date')
    principalDue = fields.Float(attribute='principal_due')
    interestDue = fields.Float(attribute='interest_due')
    lateFee = fields.Float(attribute='late_fee')
    totalDue = fields.Float(attribute='total_due')
    principalPaid = fields.Float(attribute='principal_paid')
    interestPaid = fields.Float(attribute='interest_paid')
    lateFeePaid = fields.Float(attribute='late_fee_paid')
    status = fields.String()
    paidAt = fields.DateTime(attribute='paid_at', allow_none=True)


class PaymentSchema(Schema):
    id = fields.UUID(dump_only=True)
    loan = fields.Nested(LoanSchema)
    scheduleId = fields.UUID(attribute='schedule_id', allow_none=True)
    amount = fields.Float()
    paymentType = fields.String(attribute='payment_type')
    paymentMethod = fields.String(attribute='payment_method')
    referenceNumber = fields.String(attribute='reference_number', allow_none=True)
    receivedBy = fields.Nested(UserSchema, attribute='received_by')
    notes = fields.String(allow_none=True)
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)


class PaymentCreateSchema(Schema):
    loanId = fields.UUID(required=True, data_key='loan_id')
    scheduleId = fields.UUID(data_key='schedule_id', allow_none=True)
    amount = fields.Float(required=True)
    paymentType = fields.String(required=True, data_key='payment_type')
    paymentMethod = fields.String(required=True, data_key='payment_method')
    referenceNumber = fields.String(data_key='reference_number', allow_none=True)
    notes = fields.String(allow_none=True)


class DocumentSchema(Schema):
    id = fields.UUID(dump_only=True)
    loanId = fields.UUID(attribute='loan_id')
    documentType = fields.String(attribute='document_type')
    fileName = fields.String(attribute='file_name', allow_none=True)
    filePath = fields.String(attribute='file_path', allow_none=True)
    status = fields.String()
    version = fields.Integer()
    uploadedBy = fields.Nested(UserSchema, attribute='uploaded_by', dump_only=True)
    uploadedAt = fields.DateTime(attribute='uploaded_at', dump_only=True)
    acceptedBy = fields.Nested(UserSchema, attribute='accepted_by', dump_only=True)
    acceptedAt = fields.DateTime(attribute='accepted_at', dump_only=True)
    notes = fields.String(allow_none=True)
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)


class CollectionActionSchema(Schema):
    id = fields.UUID(dump_only=True)
    loanId = fields.UUID(attribute='loan_id')
    actionType = fields.String(attribute='action_type')
    contactedPerson = fields.String(attribute='contacted_person', allow_none=True)
    contactPhone = fields.String(attribute='contact_phone', allow_none=True)
    outcome = fields.String(allow_none=True)
    promiseAmount = fields.Float(attribute='promise_amount', allow_none=True)
    promiseDate = fields.Date(attribute='promise_date', allow_none=True)
    extensionDate = fields.Date(attribute='extension_date', allow_none=True)
    performedBy = fields.Nested(UserSchema, attribute='performed_by')
    notes = fields.String(allow_none=True)
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)


class CollectionActionCreateSchema(Schema):
    actionType = fields.String(required=True, data_key='action_type')
    contactedPerson = fields.String(data_key='contacted_person', allow_none=True)
    contactPhone = fields.String(data_key='contact_phone', allow_none=True)
    outcome = fields.String(allow_none=True)
    promiseAmount = fields.Float(data_key='promise_amount', allow_none=True)
    promiseDate = fields.Date(data_key='promise_date', allow_none=True)
    extensionDate = fields.Date(data_key='extension_date', allow_none=True)
    notes = fields.String(allow_none=True)


# Pagination wrapper schema
class PaginatedSchema(Schema):
    data = fields.List(fields.Dict())
    total = fields.Integer()
    page = fields.Integer()
    pageSize = fields.Integer()
    totalPages = fields.Integer()


# Login/Register schemas
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    rememberMe = fields.Boolean(load_default=False)


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    fullName = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
    confirmPassword = fields.String(required=True, load_only=True)

    @validates('confirmPassword')
    def validate_passwords_match(self, value):
        if value != self.context.get('password'):
            raise ValidationError('Passwords do not match')


class AuthResponseSchema(Schema):
    user = fields.Nested(UserSchema)
    accessToken = fields.String()
    refreshToken = fields.String()
