import api from './api';
import type { DashboardMetrics } from '@/types';
import { API_ENDPOINTS } from '@/lib/constants';

export const dashboardService = {
  async getMetrics(): Promise<DashboardMetrics> {
    const response = await api.get<DashboardMetrics>(`${API_ENDPOINTS.DASHBOARD}/metrics`);
    return response.data;
  },

  async getPortfolioSummary(): Promise<{ portfolioTrend: { month: string; value: number }[] }> {
    const response = await api.get(`${API_ENDPOINTS.DASHBOARD}/portfolio`);
    return response.data;
  },
};

export default dashboardService;
