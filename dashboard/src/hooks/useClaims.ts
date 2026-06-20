import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { claimService } from '../services/claimService';
import type { ClaimDecision } from '../services/claimService';
import toast from 'react-hot-toast';

export function useClaims() {
  return useQuery({
    queryKey: ['claims'],
    queryFn:  claimService.listClaims,
    refetchInterval: 30_000,
  });
}

export function useClaim(claimId: string) {
  return useQuery({
    queryKey: ['claim', claimId],
    queryFn:  () => claimService.getClaim(claimId),
    enabled:  !!claimId,
  });
}

export function useFraudReport(claimId: string) {
  return useQuery({
    queryKey: ['fraud', claimId],
    queryFn:  () => claimService.getFraudReport(claimId),
    enabled:  !!claimId,
    refetchInterval: 10_000,
  });
}

export function useClaimDecision(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (decision: ClaimDecision) =>
      claimService.submitDecision(claimId, decision),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['claims'] });
      qc.invalidateQueries({ queryKey: ['claim', claimId] });
      toast.success('Decision recorded successfully');
    },
    onError: () => toast.error('Failed to submit decision'),
  });
}