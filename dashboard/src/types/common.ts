export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
}

export interface ApiError {
  success: false;
  code: string;
  detail: string | Record<string, string>[];
}

export type UserRole = 'farmer' | 'officer' | 'admin';

export type Lang = 'en' | 'hi';

export interface SelectOption {
  label: string;
  value: string;
}