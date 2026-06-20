import { useQuery } from '@tanstack/react-query';
import { adminService } from '../services/adminService';

export function useAdminStats() {
  return useQuery({
    queryKey: ['admin', 'stats'],
    queryFn:  adminService.getStats,
    refetchInterval: 60_000,
  });
}

export function useUsers(role?: string) {
  return useQuery({
    queryKey: ['users', role],
    queryFn:  () => adminService.getUsers(role),
  });
}