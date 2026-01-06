// Business Rules
export const MIN_LOAN_AMOUNT = 10000; // Q10,000
export const MAX_LTV = 0.40; // 40%
export const DEFAULT_INTEREST_RATE = 0.10; // 10% monthly
export const LATE_FEE_RATE = 0.05; // 5% late fee
export const GRACE_PERIOD_DAYS = 5;
export const DEFAULT_TRIGGER_DAYS = 15;
export const LEGAL_READY_DAYS = 30;

// Guatemala Departments
export const DEPARTMENTS = [
  'Guatemala',
  'El Progreso',
  'Sacatepéquez',
  'Chimaltenango',
  'Escuintla',
  'Santa Rosa',
  'Sololá',
  'Totonicapán',
  'Quetzaltenango',
  'Suchitepéquez',
  'Retalhuleu',
  'San Marcos',
  'Huehuetenango',
  'Quiché',
  'Baja Verapaz',
  'Alta Verapaz',
  'Petén',
  'Izabal',
  'Zacapa',
  'Chiquimula',
  'Jalapa',
  'Jutiapa',
] as const;

// Loan Status Options
export const LOAN_STATUSES = [
  { value: 'Draft', label: 'Borrador' },
  { value: 'UnderReview', label: 'En Revisión' },
  { value: 'Approved', label: 'Aprobado' },
  { value: 'Active', label: 'Activo' },
  { value: 'Matured', label: 'Vencido' },
  { value: 'Defaulted', label: 'En Mora' },
  { value: 'LegalReady', label: 'Listo para Legal' },
  { value: 'Closed', label: 'Cerrado' },
] as const;

export const LOAN_STATUS_OPTIONS = LOAN_STATUSES;

// Risk Tier Options
export const RISK_TIERS = [
  { value: 'Low', label: 'Bajo' },
  { value: 'Medium', label: 'Medio' },
  { value: 'High', label: 'Alto' },
] as const;

// Verification Status Options
export const VERIFICATION_STATUSES = [
  { value: 'Pending', label: 'Pendiente' },
  { value: 'Verified', label: 'Verificado' },
  { value: 'Rejected', label: 'Rechazado' },
] as const;

export const VERIFICATION_STATUS_OPTIONS = VERIFICATION_STATUSES;

// Property Type Options
export const PROPERTY_TYPES = [
  { value: 'House', label: 'Casa' },
  { value: 'Apartment', label: 'Apartamento' },
  { value: 'Land', label: 'Terreno' },
  { value: 'Commercial', label: 'Comercial' },
  { value: 'Industrial', label: 'Industrial' },
  { value: 'Agricultural', label: 'Agrícola' },
] as const;

export const PROPERTY_TYPE_OPTIONS = PROPERTY_TYPES;

// Payment Type Options
export const PAYMENT_TYPES = [
  { value: 'Principal', label: 'Capital' },
  { value: 'Interest', label: 'Interés' },
  { value: 'LateFee', label: 'Mora' },
  { value: 'Other', label: 'Otro' },
] as const;

export const PAYMENT_TYPE_OPTIONS = PAYMENT_TYPES;

// Payment Method Options
export const PAYMENT_METHODS = [
  { value: 'Cash', label: 'Efectivo' },
  { value: 'Transfer', label: 'Transferencia' },
  { value: 'Check', label: 'Cheque' },
] as const;

export const PAYMENT_METHOD_OPTIONS = PAYMENT_METHODS;

// Payment Status Options
export const PAYMENT_STATUSES = [
  { value: 'Pending', label: 'Pendiente' },
  { value: 'Paid', label: 'Pagado' },
  { value: 'Partial', label: 'Parcial' },
  { value: 'Overdue', label: 'Vencido' },
] as const;

export const PAYMENT_STATUS_OPTIONS = PAYMENT_STATUSES;

// Document Type Options
export const DOCUMENT_TYPES = [
  { value: 'MutuoMercantil', label: 'Mutuo Mercantil' },
  { value: 'Pagare', label: 'Pagaré' },
  { value: 'PromesaCompraventa', label: 'Promesa de Compraventa' },
  { value: 'DPI', label: 'DPI' },
  { value: 'IncomeProof', label: 'Comprobante de Ingresos' },
  { value: 'Appraisal', label: 'Avalúo' },
  { value: 'Other', label: 'Otro' },
] as const;

// Collection Action Type Options
export const COLLECTION_ACTION_TYPES = [
  { value: 'PhoneCall', label: 'Llamada Telefónica' },
  { value: 'Visit', label: 'Visita' },
  { value: 'Letter', label: 'Carta' },
  { value: 'PaymentPromise', label: 'Promesa de Pago' },
  { value: 'Extension', label: 'Prórroga' },
  { value: 'LegalNotice', label: 'Notificación Legal' },
] as const;

// Role Names
export const ROLES = {
  ADMIN: 'Admin',
  CREDIT_OFFICER: 'CreditOfficer',
  LEGAL: 'Legal',
  COLLECTIONS: 'Collections',
  BORROWER: 'Borrower',
} as const;

// Role Labels (Spanish)
export const ROLE_LABELS: Record<string, string> = {
  Admin: 'Administrador',
  CreditOfficer: 'Oficial de Crédito',
  Legal: 'Legal',
  Collections: 'Cobros',
  Borrower: 'Prestatario',
};

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    REFRESH: '/api/auth/refresh',
    LOGOUT: '/api/auth/logout',
    ME: '/api/auth/me',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    RESET_PASSWORD: '/api/auth/reset-password',
  },
  LOANS: '/api/loans',
  BORROWERS: '/api/borrowers',
  PROPERTIES: '/api/properties',
  PAYMENTS: '/api/payments',
  COLLECTIONS: '/api/collections',
  DOCUMENTS: '/api/documents',
  DASHBOARD: '/api/dashboard',
} as const;

// Route Paths - static routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  DASHBOARD: '/dashboard',
  LOANS: '/loans',
  LOAN_CREATE: '/loans/new',
  BORROWERS: '/borrowers',
  PROPERTIES: '/properties',
  PAYMENTS: '/payments',
  PAYMENTS_OVERDUE: '/payments/overdue',
  COLLECTIONS: '/collections',
  DOCUMENTS: '/documents',
  MY_LOANS: '/my-loans',
  // Dynamic route functions
  LOAN_DETAIL: (id: string) => `/loans/${id}`,
  LOAN_EDIT: (id: string) => `/loans/${id}/edit`,
  LOAN_NEW: '/loans/new',
  BORROWER_NEW: '/borrowers/new',
  BORROWER_DETAIL: (id: string) => `/borrowers/${id}`,
  BORROWER_EDIT: (id: string) => `/borrowers/${id}/edit`,
  PROPERTY_NEW: '/properties/new',
  PROPERTY_DETAIL: (id: string) => `/properties/${id}`,
  PROPERTY_EDIT: (id: string) => `/properties/${id}/edit`,
  PAYMENT_NEW: '/payments/new',
  PAYMENT_DETAIL: (id: string) => `/payments/${id}`,
  COLLECTION_DETAIL: (id: string) => `/collections/${id}`,
  COLLECTION_NEW: (loanId: string) => `/collections/new/${loanId}`,
  DOCUMENT_NEW: '/documents/new',
} as const;
