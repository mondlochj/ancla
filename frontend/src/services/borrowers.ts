import api from './api';
import type { Borrower, BorrowerFormData, Loan, PaginatedResponse, BorrowerFilters } from '@/types';
import { API_ENDPOINTS } from '@/lib/constants';

export const borrowersService = {
  async getBorrowers(filters?: BorrowerFilters): Promise<PaginatedResponse<Borrower>> {
    const response = await api.get<PaginatedResponse<Borrower>>(API_ENDPOINTS.BORROWERS, { params: filters });
    return response.data;
  },

  async getBorrower(id: string): Promise<Borrower> {
    const response = await api.get<Borrower>(`${API_ENDPOINTS.BORROWERS}/${id}`);
    return response.data;
  },

  async createBorrower(data: BorrowerFormData): Promise<Borrower> {
    const response = await api.post<Borrower>(API_ENDPOINTS.BORROWERS, data);
    return response.data;
  },

  async updateBorrower(id: string, data: Partial<BorrowerFormData>): Promise<Borrower> {
    const response = await api.put<Borrower>(`${API_ENDPOINTS.BORROWERS}/${id}`, data);
    return response.data;
  },

  async verifyBorrower(id: string, status: 'Verified' | 'Rejected'): Promise<Borrower> {
    const response = await api.post<Borrower>(`${API_ENDPOINTS.BORROWERS}/${id}/verify`, { status });
    return response.data;
  },

  async getBorrowerLoans(id: string): Promise<{ data: Loan[] }> {
    const response = await api.get<{ data: Loan[] }>(`${API_ENDPOINTS.BORROWERS}/${id}/loans`);
    return response.data;
  },
};

export default borrowersService;
