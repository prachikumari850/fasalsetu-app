import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../../components/layout/PageHeader';
import { Card } from '../../../components/ui/Card';
import { TrustScoreBadge } from '../../../components/ui/TrustScoreBadge';
import { StatusBadge } from '../../../components/ui/StatusBadge';
import { Skeleton } from '../../../components/ui/Skeleton';
import { useClaims } from '../../../hooks/useClaims';
import { formatDate } from '../../../utils/format';
import { ShieldExclamationIcon } from '@heroicons/react/24/outline';

export function FraudDashboardPage() {
  const { data: claims, isLoading } = useClaims();
  const navigate = useNavigate();

  const highRisk = (claims ?? []).filter(
    c => c.trust_score !== null && c.trust_score < 40
  );
  const medRisk = (claims ?? []).filter(
    c => c.trust_score !== null && c.trust_score >= 40 && c.trust_score < 60
  );
  const lowRisk = (claims ?? []).filter(
    c => c.trust_score !== null && c.trust_score >= 60
  );
  const unanalyzed = (claims ?? []).filter(c => c.trust_score === null);

  const getRiskLabel = (score: number | null) => {
    if (score === null) return { label: 'Pending', color: 'text-ink-hint' };
    if (score < 40)  return { label: 'High Risk',  color: 'text-danger' };
    if (score < 60)  return { label: 'Medium Risk', color: 'text-warning' };
    return               { label: 'Low Risk',   color: 'text-success' };
  };

  return (
    <div>
      <PageHeader
        title="Fraud Detection"
        subtitle="Trust scores and risk analysis for all claims"
      />

      {/* Risk Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'High Risk',   count: highRisk.length,  color: 'bg-red-50 border-red-200 text-danger' },
          { label: 'Medium Risk', count: medRisk.length,   color: 'bg-amber-50 border-amber-200 text-warning' },
          { label: 'Low Risk',    count: lowRisk.length,   color: 'bg-green-50 border-green-200 text-success' },
          { label: 'Unanalyzed', count: unanalyzed.length, color: 'bg-gray-50 border-gray-200 text-ink-secondary' },
        ].map(item => (
          <div key={item.label}
            className={`rounded-card border p-4 flex flex-col items-center justify-center ${item.color}`}>
            <span className="text-3xl font-bold">{isLoading ? '—' : item.count}</span>
            <span className="text-sm font-medium mt-1">{item.label}</span>
          </div>
        ))}
      </div>

      {/* Claims with risk scores */}
      <Card padding={false}>
        <div className="px-5 py-4 border-b border-border">
          <h3 className="section-title">Claims Risk Overview</h3>
        </div>

        {isLoading ? (
          <div className="p-4 space-y-3">
            {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-12 rounded-lg" />)}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted">
                  <th className="text-left px-5 py-3 label">Claim ID</th>
                  <th className="text-left px-5 py-3 label">Damage Type</th>
                  <th className="text-left px-5 py-3 label">Claim Status</th>
                  <th className="text-left px-5 py-3 label">Trust Score</th>
                  <th className="text-left px-5 py-3 label">Risk Level</th>
                  <th className="text-left px-5 py-3 label">Submitted</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {(claims ?? [])
                  .sort((a, b) => (a.trust_score ?? 100) - (b.trust_score ?? 100))
                  .map(claim => {
                    const risk = getRiskLabel(claim.trust_score);
                    const grade = claim.trust_score !== null
                      ? claim.trust_score >= 80 ? 'A'
                      : claim.trust_score >= 60 ? 'B'
                      : claim.trust_score >= 40 ? 'C'
                      : claim.trust_score >= 20 ? 'D' : 'F'
                      : null;

                    return (
                      <tr
                        key={claim.id}
                        onClick={() => navigate(`/officer/claims/${claim.id}`)}
                        className="hover:bg-muted cursor-pointer transition-colors"
                      >
                        <td className="px-5 py-3 font-mono text-xs text-ink-secondary">
                          {claim.id.slice(0, 8)}...
                        </td>
                        <td className="px-5 py-3 capitalize">{claim.damage_type}</td>
                        <td className="px-5 py-3">
                          <StatusBadge status={claim.status} />
                        </td>
                        <td className="px-5 py-3">
                          <TrustScoreBadge score={claim.trust_score} grade={grade} />
                        </td>
                        <td className={`px-5 py-3 font-medium ${risk.color}`}>
                          {risk.label}
                        </td>
                        <td className="px-5 py-3 text-ink-secondary">
                          {claim.submitted_at ? formatDate(claim.submitted_at) : '—'}
                        </td>
                        <td className="px-5 py-3 text-right text-primary-700 font-medium">
                          Review →
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}