import { format, formatDistanceToNow, parseISO } from 'date-fns';

export function formatDate(dateString: string): string {
  return format(parseISO(dateString), 'dd MMM yyyy');
}

export function formatDateTime(dateString: string): string {
  return format(parseISO(dateString), 'dd MMM yyyy, hh:mm a');
}

export function formatRelative(dateString: string): string {
  return formatDistanceToNow(parseISO(dateString), { addSuffix: true });
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatArea(acres: number): string {
  return `${acres.toFixed(2)} acres`;
}

export function formatScore(score: number): string {
  return `${score.toFixed(1)}/100`;
}

export function getTrustGrade(score: number): 'A' | 'B' | 'C' | 'D' | 'F' {
  if (score >= 80) return 'A';
  if (score >= 60) return 'B';
  if (score >= 40) return 'C';
  if (score >= 20) return 'D';
  return 'F';
}

export function getClaimStatusLabel(status: string): string {
  const map: Record<string, string> = {
    draft: 'Draft',
    submitted: 'Submitted',
    under_review: 'Under Review',
    approved: 'Approved',
    rejected: 'Rejected',
    needs_inspection: 'Needs Inspection',
  };
  return map[status] ?? status;
}

export function getDamageTypeLabel(type: string): string {
  const map: Record<string, string> = {
    drought: 'Drought',
    flood: 'Flood',
    hail: 'Hail',
    pest: 'Pest Attack',
    disease: 'Disease',
    fire: 'Fire',
    other: 'Other',
  };
  return map[type] ?? type;
}