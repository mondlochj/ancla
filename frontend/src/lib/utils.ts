import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'GTQ',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount).replace('GTQ', 'Q');
}

export function formatDate(dateString: string): string {
  return new Intl.DateTimeFormat('es-GT', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(dateString));
}

export function formatDateTime(dateString: string): string {
  return new Intl.DateTimeFormat('es-GT', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(dateString));
}

export function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

export function maskDpi(dpi: string): string {
  if (dpi.length <= 4) return dpi;
  return '*'.repeat(dpi.length - 4) + dpi.slice(-4);
}

export function getStatusColor(status: string): string {
  const statusMap: Record<string, string> = {
    Draft: 'status-draft',
    UnderReview: 'status-under-review',
    Approved: 'status-approved',
    Active: 'status-active',
    Matured: 'status-matured',
    Defaulted: 'status-defaulted',
    LegalReady: 'status-legal-ready',
    Closed: 'status-closed',
    Pending: 'status-pending',
    Verified: 'status-verified',
    Rejected: 'status-rejected',
    Paid: 'status-approved',
    Partial: 'status-under-review',
    Overdue: 'status-defaulted',
  };
  return statusMap[status] || 'status-draft';
}

export function calculateLtv(loanAmount: number, propertyValue: number): number {
  if (propertyValue <= 0) return 0;
  return loanAmount / propertyValue;
}

export function calculateMonthlyPayment(
  principal: number,
  annualRate: number,
  termMonths: number
): number {
  const monthlyRate = annualRate / 12;
  if (monthlyRate === 0) return principal / termMonths;

  const payment =
    (principal * monthlyRate * Math.pow(1 + monthlyRate, termMonths)) /
    (Math.pow(1 + monthlyRate, termMonths) - 1);

  return payment;
}

export function calculateTotalInterest(
  principal: number,
  monthlyPayment: number,
  termMonths: number
): number {
  return monthlyPayment * termMonths - principal;
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function generateReferenceNumber(): string {
  const date = new Date();
  const year = date.getFullYear().toString().slice(-2);
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const random = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `AC-${year}${month}-${random}`;
}

export const GUATEMALA_DEPARTMENTS = [
  'Guatemala',
  'Alta Verapaz',
  'Baja Verapaz',
  'Chimaltenango',
  'Chiquimula',
  'El Progreso',
  'Escuintla',
  'Huehuetenango',
  'Izabal',
  'Jalapa',
  'Jutiapa',
  'Petén',
  'Quetzaltenango',
  'Quiché',
  'Retalhuleu',
  'Sacatepéquez',
  'San Marcos',
  'Santa Rosa',
  'Sololá',
  'Suchitepéquez',
  'Totonicapán',
  'Zacapa',
];
