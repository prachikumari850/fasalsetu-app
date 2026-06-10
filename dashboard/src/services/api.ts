import axios, { type AxiosInstance, type AxiosError } from 'axios';
import toast from 'react-hot-toast';

const BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: BASE_URL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 30_000,
  });

  // Request: attach JWT
  client.interceptors.request.use((config) => {
    const token = localStorage.getItem('fs_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Response: normalize errors
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError<{ detail: string; code: string }>) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('fs_token');
        localStorage.removeItem('fs_user');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      if (error.response?.status === 403) {
        toast.error('You do not have permission to perform this action.');
      } else if (error.response?.status === 404) {
        toast.error('Resource not found.');
      } else if (error.response?.status === 422) {
        toast.error('Validation error. Please check your input.');
      } else if (error.response && error.response.status >= 500) {
        toast.error('Server error. Please try again later.');
      } else if (!error.response) {
        toast.error('Network error. Check your connection.');
      }

      return Promise.reject(error);
    }
  );

  return client;
}

export const api = createApiClient();