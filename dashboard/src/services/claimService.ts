import { api } from './api';
import type { ApiResponse } from '../types/common';

export interface ClaimSummary {
  id: string;
  farm_id: string;
  status: string;
  damage_type: string;
  trust_score: number | null;
  submitted_at: string | null;
}

export interface ClaimDetail {
  id: string;
  farm_id: string;
  farmer_id: string;
  status: string;
  damage_type: string;
  damage_description: string | null;
  estimated_loss: number | null;
  affected_acres: number | null;
  trust_score: number | null;
  submitted_at: string | null;
  reviewed_at: string | null;
  officer_notes: string | null;
  fraud_analyzed: boolean;
  fraud_score: number | null;
  fraud_flags: string[];
}

export interface FraudReport {
  claim_id: string;
  status: string;
  trust_score: number | null;
  fraud_score: number | null;
  grade: string | null;
  gps_score: number;
  lifecycle_score: number;
  weather_score: number;
  hash_score: number;
  document_score: number;
  flags: string[];
  recommendation: string;
  generated_at: string | null;
}

export interface ClaimDecision {
  status: 'approved' | 'rejected' | 'needs_inspection' | 'under_review';
  officer_notes?: string;
}

export const claimService = {
  async listClaims(): Promise<ClaimSummary[]> {
    const res = await api.get<ApiResponse<ClaimSummary[]>>('/claims');
    return res.data.data;
  },

  async getClaim(claimId: string): Promise<ClaimDetail> {
    const res = await api.get<ApiResponse<ClaimDetail>>(`/claims/${claimId}`);
    return res.data.data;
  },

  async getFraudReport(claimId: string): Promise<FraudReport> {
    const res = await api.get<ApiResponse<FraudReport>>(`/fraud/${claimId}`);
    return res.data.data;
  },

  async submitDecision(claimId: string, decision: ClaimDecision): Promise<void> {
    await api.put(`/claims/${claimId}/decision`, decision);
  },

  async triggerFraudAnalysis(claimId: string): Promise<void> {
    await api.post(`/fraud/analyze/${claimId}`);
  },

  async getTrustScore(farmId: string): Promise<{
    score: number | null;
    grade: string | null;
    breakdown: Record<string, unknown> | null;
  }> {
    const res = await api.get(`/fraud/trust/${farmId}`);
    return res.data.data;
  },
};