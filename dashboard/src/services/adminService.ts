import { api } from './api';
import type { ApiResponse } from '../types/common';
import type { User } from '../types/auth';

export interface AdminStats {
  total_farmers: number;
  total_farms: number;
  total_claims: number;
  pending_claims: number;
  approved_claims: number;
  rejected_claims: number;
  avg_trust_score: number;
}

export const adminService = {
  async getStats(): Promise<AdminStats> {
    const res = await api.get<ApiResponse<AdminStats>>('/admin/analytics/overview');
    return res.data.data;
  },

  async getUsers(role?: string): Promise<User[]> {
    const params = role ? { role } : {};
    const res = await api.get<ApiResponse<User[]>>('/admin/users', { params });
    return res.data.data;
  },

  async updateUserRole(userId: string, role: string): Promise<void> {
    await api.put(`/admin/users/${userId}/role`, { role });
  },
};