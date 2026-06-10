export type ClaimStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'needs_inspection';

export type DamageType =
  | 'drought'
  | 'flood'
  | 'hail'
  | 'pest'
  | 'disease'
  | 'fire'
  | 'other';

export interface ClaimImage {
  id: string;
  claim_id: string;
  storage_url: string;
  latitude: number;
  longitude: number;
  captured_at: string;
}

export interface FraudReport {
  id: string;
  claim_id: string;
  gps_score: number;
  lifecycle_score: number;
  weather_score: number;
  hash_score: number;
  document_score: number;
  total_fraud_score: number;
  flags: string[];
  weather_data: Record<string, unknown> | null;
  generated_at: string;
}

export interface Claim {
  id: string;
  farm_id: string;
  farmer_id: string;
  status: ClaimStatus;
  damage_type: DamageType;
  damage_description: string | null;
  estimated_loss: number | null;
  affected_acres: number | null;
  trust_score: number | null;
  officer_id: string | null;
  officer_notes: string | null;
  submitted_at: string | null;
  reviewed_at: string | null;
  created_at: string;
  images: ClaimImage[];
  fraud_report?: FraudReport;
}