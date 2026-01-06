import api from './api';
import type { Payment, PaymentFormData, PaymentSchedule, PaginatedResponse, PaymentFilters } from '@/types';
import { API_ENDPOINTS } from '@/lib/constants';

export const paymentsService = {
  async getPayments(filters?: PaymentFilters): Promise<PaginatedResponse<Payment>> {
    const response = await api.get<PaginatedResponse<Payment>>(API_ENDPOINTS.PAYMENTS, { params: filters });
    return response.data;
  },

  async getPayment(id: string): Promise<Payment> {
    const response = await api.get<Payment>(`${API_ENDPOINTS.PAYMENTS}/${id}`);
    return response.data;
  },

  async createPayment(data: PaymentFormData): Promise<Payment> {
    const response = await api.post<Payment>(API_ENDPOINTS.PAYMENTS, data);
    return response.data;
  },

  async getOverduePayments(): Promise<{ data: PaymentSchedule[]; total: number }> {
    const response = await api.get<{ data: PaymentSchedule[]; total: number }>(`${API_ENDPOINTS.PAYMENTS}/overdue`);
    return response.data;
  },

  async getLoanSchedule(loanId: string): Promise<{ data: PaymentSchedule[] }> {
    const response = await api.get<{ data: PaymentSchedule[] }>(`${API_ENDPOINTS.LOANS}/${loanId}/schedule`);
    return response.data;
  },
};

export default paymentsService;
