import api from './api';
import type { Loan, LoanFormData, PaymentSchedule, PaginatedResponse, LoanFilters } from '@/types';
import { API_ENDPOINTS } from '@/lib/constants';

export const loansService = {
  async getLoans(filters?: LoanFilters): Promise<PaginatedResponse<Loan>> {
    const response = await api.get<PaginatedResponse<Loan>>(API_ENDPOINTS.LOANS, { params: filters });
    return response.data;
  },

  async getLoan(id: string): Promise<Loan> {
    const response = await api.get<Loan>(`${API_ENDPOINTS.LOANS}/${id}`);
    return response.data;
  },

  async createLoan(data: LoanFormData): Promise<Loan> {
    const response = await api.post<Loan>(API_ENDPOINTS.LOANS, data);
    return response.data;
  },

  async updateLoan(id: string, data: Partial<LoanFormData>): Promise<Loan> {
    const response = await api.put<Loan>(`${API_ENDPOINTS.LOANS}/${id}`, data);
    return response.data;
  },

  async submitLoan(id: string): Promise<Loan> {
    const response = await api.post<Loan>(`${API_ENDPOINTS.LOANS}/${id}/submit`);
    return response.data;
  },

  async approveLoan(id: string, notes?: string): Promise<Loan> {
    const response = await api.post<Loan>(`${API_ENDPOINTS.LOANS}/${id}/approve`, { notes });
    return response.data;
  },

  async activateLoan(id: string): Promise<Loan> {
    const response = await api.post<Loan>(`${API_ENDPOINTS.LOANS}/${id}/activate`);
    return response.data;
  },

  async getLoanSchedule(id: string): Promise<{ data: PaymentSchedule[] }> {
    const response = await api.get<{ data: PaymentSchedule[] }>(`${API_ENDPOINTS.LOANS}/${id}/schedule`);
    return response.data;
  },

  async getMyLoans(): Promise<{ data: Loan[]; total: number }> {
    const response = await api.get<{ data: Loan[]; total: number }>('/api/my-loans');
    return response.data;
  },
};

export default loansService;
