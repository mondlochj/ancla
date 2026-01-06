import api from './api';
import type { Property, PropertyFormData, PaginatedResponse } from '@/types';
import { API_ENDPOINTS } from '@/lib/constants';

interface PropertyFilters {
  verificationStatus?: string;
  department?: string;
  search?: string;
  page?: number;
  pageSize?: number;
}

export const propertiesService = {
  async getProperties(filters?: PropertyFilters): Promise<PaginatedResponse<Property>> {
    const response = await api.get<PaginatedResponse<Property>>(API_ENDPOINTS.PROPERTIES, { params: filters });
    return response.data;
  },

  async getProperty(id: string): Promise<Property> {
    const response = await api.get<Property>(`${API_ENDPOINTS.PROPERTIES}/${id}`);
    return response.data;
  },

  async createProperty(data: PropertyFormData): Promise<Property> {
    const response = await api.post<Property>(API_ENDPOINTS.PROPERTIES, data);
    return response.data;
  },

  async updateProperty(id: string, data: Partial<PropertyFormData>): Promise<Property> {
    const response = await api.put<Property>(`${API_ENDPOINTS.PROPERTIES}/${id}`, data);
    return response.data;
  },

  async verifyProperty(id: string, status: 'Verified' | 'Rejected'): Promise<Property> {
    const response = await api.post<Property>(`${API_ENDPOINTS.PROPERTIES}/${id}/verify`, { status });
    return response.data;
  },
};

export default propertiesService;
