import api from './api';
import type { CollectionAction, PaginatedResponse } from '@/types';

interface CollectionFilters {
  search?: string;
  actionType?: string;
  status?: string;
  loanId?: string;
  page?: number;
  pageSize?: number;
}

interface CollectionFormData {
  loanId: string;
  actionType: string;
  actionDate: string;
  notes: string;
  result?: string;
  promisedAmount?: number;
  promisedDate?: string;
  followUpDate?: string;
  followUpNotes?: string;
}

export const collectionsService = {
  async getCollections(filters?: CollectionFilters): Promise<PaginatedResponse<CollectionAction>> {
    const response = await api.get<PaginatedResponse<CollectionAction>>('/api/collections', { params: filters });
    return response.data;
  },

  async getCollection(id: string): Promise<CollectionAction> {
    const response = await api.get<CollectionAction>(`/api/collections/${id}`);
    return response.data;
  },

  async createCollection(data: CollectionFormData): Promise<CollectionAction> {
    const response = await api.post<CollectionAction>('/api/collections', data);
    return response.data;
  },

  async getLoanCollections(loanId: string): Promise<{ data: CollectionAction[] }> {
    const response = await api.get<{ data: CollectionAction[] }>(`/api/loans/${loanId}/collections`);
    return response.data;
  },
};

export default collectionsService;
