// User and Auth Types
export interface User {
  id: string;
  email: string;
  fullName: string;
  role: Role;
  isVerified: boolean;
  createdAt: string;
  lastLogin?: string;
}

export interface Role {
  id: string;
  name: 'Admin' | 'CreditOfficer' | 'Legal' | 'Collections' | 'Borrower';
  permissions: Record<string, string[]>;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  email: string;
  fullName: string;
  password: string;
  confirmPassword: string;
}

// Loan Types
export type LoanStatus =
  | 'Draft'
  | 'UnderReview'
  | 'Approved'
  | 'Active'
  | 'Matured'
  | 'Defaulted'
  | 'LegalReady'
  | 'Closed';

export interface LoanProduct {
  id: string;
  name: string;
  description?: string;
  minAmount: number;
  maxAmount: number;
  minTermMonths: number;
  maxTermMonths: number;
  defaultInterestRate: number;
  isActive: boolean;
}

export interface Loan {
  id: string;
  referenceNumber: string;
  borrower: Borrower;
  property: Property;
  loanProduct: LoanProduct;
  amount: number;
  termMonths: number;
  interestRate: number;
  ltv: number;
  status: LoanStatus;
  approvedBy?: User;
  approvedAt?: string;
  activatedAt?: string;
  maturityDate?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface LoanFormData {
  borrowerId: string;
  propertyId: string;
  loanProductId: string;
  amount: number;
  termMonths: number;
  interestRate: number;
}

export interface LoanSummary {
  totalLoans: number;
  activeLoans: number;
  portfolioValue: number;
  defaultRate: number;
  averageLtv: number;
  monthlyInterest: number;
}

// Borrower Types
export type RiskTier = 'Low' | 'Medium' | 'High';
export type VerificationStatus = 'Pending' | 'Verified' | 'Rejected';

export interface Borrower {
  id: string;
  dpi: string;
  firstName: string;
  lastName: string;
  fullName: string;
  email?: string;
  phone: string;
  alternatePhone?: string;
  address: string;
  municipality: string;
  department: string;
  occupation?: string;
  employer?: string;
  monthlyIncome?: number;
  riskTier: RiskTier;
  verificationStatus: VerificationStatus;
  verifiedBy?: User;
  verifiedAt?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface BorrowerFormData {
  dpi: string;
  firstName: string;
  lastName: string;
  email?: string;
  phone: string;
  alternatePhone?: string;
  address: string;
  municipality: string;
  department: string;
  occupation?: string;
  employer?: string;
  monthlyIncome?: number;
  riskTier: RiskTier;
  notes?: string;
}

// Property Types
export interface Property {
  id: string;
  finca: string;
  folio: string;
  libro: string;
  address: string;
  municipality: string;
  department: string;
  areaM2: number;
  marketValue: number;
  appraisalValue?: number;
  appraisalDate?: string;
  verificationStatus: VerificationStatus;
  verifiedBy?: User;
  verifiedAt?: string;
  latitude?: number;
  longitude?: number;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface PropertyFormData {
  finca: string;
  folio: string;
  libro: string;
  address: string;
  municipality: string;
  department: string;
  areaM2: number;
  marketValue: number;
  appraisalValue?: number;
  appraisalDate?: string;
  latitude?: number;
  longitude?: number;
  notes?: string;
}

// Payment Types
export type PaymentType = 'Principal' | 'Interest' | 'LateFee' | 'Other';
export type PaymentMethod = 'Cash' | 'Transfer' | 'Check';
export type ScheduleStatus = 'Pending' | 'Paid' | 'Partial' | 'Overdue';

export interface PaymentSchedule {
  id: string;
  loanId: string;
  dueDate: string;
  principalDue: number;
  interestDue: number;
  lateFee: number;
  totalDue: number;
  principalPaid: number;
  interestPaid: number;
  lateFeePaid: number;
  status: ScheduleStatus;
  paidAt?: string;
}

export interface Payment {
  id: string;
  loan: Loan;
  scheduleId?: string;
  amount: number;
  paymentType: PaymentType;
  paymentMethod: PaymentMethod;
  referenceNumber?: string;
  receivedBy: User;
  notes?: string;
  createdAt: string;
}

export interface PaymentFormData {
  loanId: string;
  scheduleId?: string;
  amount: number;
  paymentType: PaymentType;
  paymentMethod: PaymentMethod;
  referenceNumber?: string;
  notes?: string;
}

// Collection Types
export type CollectionStage = 'Current' | 'Reminder' | 'Grace' | 'Delinquent' | 'LegalReady';
export type CollectionActionType = 'PhoneCall' | 'Visit' | 'Letter' | 'PaymentPromise' | 'Extension' | 'LegalNotice';

export interface CollectionAction {
  id: string;
  loanId: string;
  actionType: CollectionActionType;
  contactedPerson?: string;
  contactPhone?: string;
  outcome?: string;
  promiseAmount?: number;
  promiseDate?: string;
  extensionDate?: string;
  performedBy: User;
  notes?: string;
  createdAt: string;
}

// Document Types
export type DocumentType = 'MutuoMercantil' | 'Pagare' | 'PromesaCompraventa' | 'DPI' | 'IncomeProof' | 'Appraisal' | 'Other';
export type DocumentStatus = 'Pending' | 'Uploaded' | 'Executed';

export interface Document {
  id: string;
  loanId: string;
  documentType: DocumentType;
  fileName?: string;
  filePath?: string;
  status: DocumentStatus;
  version: number;
  uploadedBy?: User;
  uploadedAt?: string;
  acceptedBy?: User;
  acceptedAt?: string;
  acceptedIp?: string;
  notes?: string;
  createdAt: string;
}

// Dashboard Types
export interface DashboardMetrics {
  totalPortfolioValue: number;
  activeLoansCount: number;
  defaultRate: number;
  averageLtv: number;
  monthlyInterestIncome: number;
  overduePaymentsCount: number;
  overdueAmount: number;
  loansByStatus: Record<LoanStatus, number>;
  loansByDepartment: Record<string, number>;
  recentLoans: Loan[];
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  statusCode: number;
}

// Filter Types
export interface LoanFilters {
  status?: LoanStatus;
  borrowerId?: string;
  search?: string;
  page?: number;
  pageSize?: number;
}

export interface BorrowerFilters {
  verificationStatus?: VerificationStatus;
  riskTier?: RiskTier;
  department?: string;
  search?: string;
  page?: number;
  pageSize?: number;
}

export interface PaymentFilters {
  loanId?: string;
  paymentType?: PaymentType;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
}
