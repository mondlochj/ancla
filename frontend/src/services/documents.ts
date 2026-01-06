import api from './api';
import type { Document, PaginatedResponse } from '@/types';

interface DocumentFilters {
  search?: string;
  documentType?: string;
  status?: string;
  loanId?: string;
  borrowerId?: string;
  propertyId?: string;
  page?: number;
  pageSize?: number;
}

export const documentsService = {
  async getDocuments(filters?: DocumentFilters): Promise<PaginatedResponse<Document>> {
    const response = await api.get<PaginatedResponse<Document>>('/api/documents', { params: filters });
    return response.data;
  },

  async getDocument(id: string): Promise<Document> {
    const response = await api.get<Document>(`/api/documents/${id}`);
    return response.data;
  },

  async uploadDocument(formData: FormData): Promise<Document> {
    const response = await api.post<Document>('/api/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async deleteDocument(id: string): Promise<void> {
    await api.delete(`/api/documents/${id}`);
  },

  async getLoanDocuments(loanId: string): Promise<{ data: Document[] }> {
    const response = await api.get<{ data: Document[] }>(`/api/loans/${loanId}/documents`);
    return response.data;
  },

  async getBorrowerDocuments(borrowerId: string): Promise<{ data: Document[] }> {
    const response = await api.get<{ data: Document[] }>(`/api/borrowers/${borrowerId}/documents`);
    return response.data;
  },
};

export default documentsService;
