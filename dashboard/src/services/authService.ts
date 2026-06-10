import { api } from './api';
import type { User } from '../types/auth';
import type { ApiResponse } from '../types/common';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export const authService = {
  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await api.post<ApiResponse<TokenResponse>>('/auth/login', {
      email,
      password,
    });
    return response.data.data;
  },

  async getMe(): Promise<User> {
    const response = await api.get<ApiResponse<User>>('/auth/me');
    return response.data.data;
  },
};