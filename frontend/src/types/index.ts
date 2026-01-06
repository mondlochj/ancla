// User and Auth Types
export interface User {
  id: string;
  email: string;
  fullName: string;
  role: string;
  isVerified: boolean;
  createdAt: string;
  lastLogin?: string;
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
  loanNumber: string;
  referenceNumber?: string;
  borrowerId?: string;
  borrower?: Borrower;
  propertyId?: string;
  property?: Property;
  loanProduct?: LoanProduct;
  amount: number;
  termMonths: number;
  interestRate: number;
  monthlyPayment?: number;
  outstandingBalance?: number;
  ltv?: number;
  status: LoanStatus;
  startDate: string;
  endDate?: string;
  approvedBy?: User;
  approvedAt?: string;
  activatedAt?: string;
  maturityDate?: string;
  daysOverdue?: number;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface LoanFormData {
  borrowerId: string;
  propertyId: string;
  loanProductId?: string;
  amount: number;
  termMonths: number;
  interestRate: number;
  startDate?: string;
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
  nit?: string;
  firstName: string;
  lastName: string;
  fullName?: string;
  email?: string;
  phone: string;
  alternatePhone?: string;
  address: string;
  municipality: string;
  department: string;
  occupation?: string;
  employer?: string;
  employerName?: string;
  employerPhone?: string;
  monthlyIncome?: number;
  riskTier?: RiskTier;
  verificationStatus: VerificationStatus;
  verifiedBy?: User;
  verifiedAt?: string;
  activeLoans?: number;
  totalLoaned?: number;
  outstandingBalance?: number;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface BorrowerFormData {
  dpi: string;
  nit?: string;
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
  employerName?: string;
  employerPhone?: string;
  monthlyIncome?: number;
  riskTier?: RiskTier;
  notes?: string;
}

// Property Types
export interface Property {
  id: string;
  registryNumber: string;
  finca?: string;
  folio?: string;
  libro?: string;
  propertyType: string;
  address: string;
  municipality: string;
  department: string;
  area?: number;
  areaM2?: number;
  constructionArea?: number;
  estimatedValue: number;
  marketValue?: number;
  appraisalValue?: number;
  appraisalDate?: string;
  lastAppraisalDate?: string;
  bedrooms?: number;
  bathrooms?: number;
  parkingSpaces?: number;
  yearBuilt?: number;
  verificationStatus: VerificationStatus;
  verifiedBy?: User;
  verifiedAt?: string;
  latitude?: number;
  longitude?: number;
  borrowerId?: string;
  borrower?: Borrower;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface PropertyFormData {
  registryNumber: string;
  finca?: string;
  folio?: string;
  libro?: string;
  propertyType: string;
  address: string;
  municipality: string;
  department: string;
  area: number;
  areaM2?: number;
  constructionArea?: number;
  estimatedValue: number;
  marketValue?: number;
  appraisalValue?: number;
  appraisalDate?: string;
  bedrooms?: number;
  bathrooms?: number;
  parkingSpaces?: number;
  yearBuilt?: number;
  latitude?: number;
  longitude?: number;
  borrowerId?: string;
  notes?: string;
}

// Payment Types
export type PaymentType = 'Principal' | 'Interest' | 'LateFee' | 'Other';
export type PaymentMethod = 'Cash' | 'Transfer' | 'Check';
export type ScheduleStatus = 'Pending' | 'Paid' | 'Partial' | 'Overdue';

export interface PaymentSchedule {
  id?: string;
  loanId: string;
  loanNumber?: string;
  borrowerName?: string;
  borrowerPhone?: string;
  borrowerEmail?: string;
  paymentNumber: number;
  dueDate: string;
  amount: number;
  principal: number;
  interest: number;
  principalDue?: number;
  interestDue?: number;
  lateFee?: number;
  totalDue?: number;
  principalPaid?: number;
  interestPaid?: number;
  lateFeePaid?: number;
  status: ScheduleStatus;
  paidAt?: string;
}

export interface Payment {
  id: string;
  loanId: string;
  loanNumber?: string;
  loan?: Loan;
  scheduleId?: string;
  amount: number;
  paymentType: string;
  paymentMethod?: string;
  dueDate?: string;
  paymentDate?: string;
  referenceNumber?: string;
  receivedBy?: User;
  status: string;
  notes?: string;
  createdAt: string;
}

export interface PaymentFormData {
  loanId: string;
  scheduleId?: string;
  amount: number;
  paymentType: string;
  paymentMethod: string;
  paymentDate: string;
  referenceNumber?: string;
  notes?: string;
}

// Collection Types
export type CollectionStage = 'Current' | 'Reminder' | 'Grace' | 'Delinquent' | 'LegalReady';
export type CollectionActionType = 'PhoneCall' | 'Visit' | 'Letter' | 'PaymentPromise' | 'Extension' | 'LegalNotice' | 'Call' | 'Email';

export interface CollectionAction {
  id: string;
  loanId: string;
  loanNumber?: string;
  borrowerName?: string;
  actionType: string;
  actionDate: string;
  contactedPerson?: string;
  contactPhone?: string;
  outcome?: string;
  result?: string;
  promiseAmount?: number;
  promisedAmount?: number;
  promiseDate?: string;
  promisedDate?: string;
  extensionDate?: string;
  followUpDate?: string;
  followUpNotes?: string;
  performedBy?: User;
  agentName?: string;
  notes?: string;
  createdAt: string;
}

// Document Types
export type DocumentType = 'MutuoMercantil' | 'Pagare' | 'PromesaCompraventa' | 'DPI' | 'IncomeProof' | 'Appraisal' | 'Other' | 'Contract' | 'PropertyDeed';
export type DocumentStatus = 'Pending' | 'Uploaded' | 'Executed' | 'Active' | 'Expired';

export interface Document {
  id: string;
  loanId?: string;
  loanNumber?: string;
  borrowerId?: string;
  borrowerName?: string;
  propertyId?: string;
  propertyNumber?: string;
  documentType: string;
  name: string;
  fileName?: string;
  filePath?: string;
  status: string;
  version?: number;
  uploadedBy?: User;
  uploadedByName?: string;
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
  verificationStatus?: string;
  riskTier?: RiskTier;
  department?: string;
  search?: string;
  page?: number;
  pageSize?: number;
}

export interface PaymentFilters {
  loanId?: string;
  paymentType?: PaymentType;
  status?: string;
  search?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
}
