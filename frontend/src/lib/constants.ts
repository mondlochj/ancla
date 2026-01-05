// Business Rules
export const MIN_LOAN_AMOUNT = 10000; // Q10,000
export const MAX_LTV = 0.40; // 40%
export const DEFAULT_INTEREST_RATE = 0.10; // 10% monthly
export const LATE_FEE_RATE = 0.05; // 5% late fee
export const GRACE_PERIOD_DAYS = 5;
export const DEFAULT_TRIGGER_DAYS = 15;
export const LEGAL_READY_DAYS = 30;

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

// Payment Type Options
export const PAYMENT_TYPES = [
  { value: 'Principal', label: 'Capital' },
  { value: 'Interest', label: 'Interés' },
  { value: 'LateFee', label: 'Mora' },
  { value: 'Other', label: 'Otro' },
] as const;

// Payment Method Options
export const PAYMENT_METHODS = [
  { value: 'Cash', label: 'Efectivo' },
  { value: 'Transfer', label: 'Transferencia' },
  { value: 'Check', label: 'Cheque' },
] as const;

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

// Route Paths
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  DASHBOARD: '/dashboard',
  LOANS: '/loans',
  LOAN_DETAIL: '/loans/:id',
  LOAN_CREATE: '/loans/create',
  BORROWERS: '/borrowers',
  BORROWER_DETAIL: '/borrowers/:id',
  BORROWER_CREATE: '/borrowers/create',
  PROPERTIES: '/properties',
  PROPERTY_DETAIL: '/properties/:id',
  PROPERTY_CREATE: '/properties/create',
  PAYMENTS: '/payments',
  PAYMENT_RECORD: '/payments/record',
  COLLECTIONS: '/collections',
  DOCUMENTS: '/documents',
  MY_LOANS: '/my-loans',
  MY_LOAN_DETAIL: '/my-loans/:id',
} as const;
