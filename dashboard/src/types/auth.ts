import type { UserRole } from './common';

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  role: UserRole;
  district: string | null;
  state: string;
  is_active: boolean;
  preferred_lang: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isOfficer: boolean;
  isAdmin: boolean;
}