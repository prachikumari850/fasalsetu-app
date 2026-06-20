import { useNavigate } from 'react-router-dom';
import {
  ClipboardDocumentListIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import { PageHeader } from '../../components/layout/PageHeader';
import { StatCard } from '../../components/charts/StatCard';
import { Card } from '../../components/ui/Card';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { TrustScoreBadge } from '../../components/ui/TrustScoreBadge';
import { Skeleton } from '../../components/ui/Skeleton';
import { useClaims } from '../../hooks/useClaims';
import { formatDate, formatCurrency } from '../../utils/format';
import { useAuth } from '../../hooks/useAuth';

export function OfficerDashboard() {
  const { data: claims, isLoading } = useClaims();
  const { user } = useAuth();
  const navigate = useNavigate();

  const submitted     = claims?.filter(c => c.status === 'submitted').length ?? 0;
  const approved      = claims?.filter(c => c.status === 'approved').length ?? 0;
  const rejected      = claims?.filter(c => c.status === 'rejected').length ?? 0;
  const needsReview   = claims?.filter(c => c.status === 'needs_inspection').length ?? 0;
  const recentClaims  = claims?.slice(0, 8) ?? [];

  return (
    <div>
      <PageHeader
        title={`Welcome, ${user?.full_name ?? 'Officer'}`}
        subtitle="Claims overview and fraud monitoring"
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="Pending Review"
          value={submitted}
          icon={<ClockIcon className="h-5 w-5" />}
          color="orange"
          isLoading={isLoading}
        />
        <StatCard
          title="Approved"
          value={approved}
          icon={<CheckCircleIcon className="h-5 w-5" />}
          color="green"
          isLoading={isLoading}
        />
        <StatCard
          title="Rejected"
          value={rejected}
          icon={<XCircleIcon className="h-5 w-5" />}
          color="red"
          isLoading={isLoading}
        />
        <StatCard
          title="Needs Inspection"
          value={needsReview}
          icon={<MagnifyingGlassIcon className="h-5 w-5" />}
          color="blue"
          isLoading={isLoading}
        />
      </div>

      {/* Recent Claims Table */}
      <Card padding={false}>
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <h3 className="section-title">Recent Claims</h3>
          <button
            onClick={() => navigate('/officer/claims')}
            className="text-sm text-primary-700 font-medium hover:underline"
          >
            View all →
          </button>
        </div>

        {isLoading ? (
          <div className="p-4 space-y-3">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-12 rounded-lg" />
            ))}
          </div>
        ) : recentClaims.length === 0 ? (
          <div className="py-12 text-center text-ink-secondary text-sm">
            No claims submitted yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted">
                  <th className="text-left px-5 py-3 label">Claim ID</th>
                  <th className="text-left px-5 py-3 label">Damage Type</th>
                  <th className="text-left px-5 py-3 label">Status</th>
                  <th className="text-left px-5 py-3 label">Trust Score</th>
                  <th className="text-left px-5 py-3 label">Submitted</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {recentClaims.map(claim => (
                  <tr
                    key={claim.id}
                    className="hover:bg-muted cursor-pointer transition-colors"
                    onClick={() => navigate(`/officer/claims/${claim.id}`)}
                  >
                    <td className="px-5 py-3 font-mono text-xs text-ink-secondary">
                      {claim.id.slice(0, 8)}...
                    </td>
                    <td className="px-5 py-3 capitalize">{claim.damage_type}</td>
                    <td className="px-5 py-3">
                      <StatusBadge status={claim.status} />
                    </td>
                    <td className="px-5 py-3">
                      <TrustScoreBadge
                        score={claim.trust_score}
                        grade={
                          claim.trust_score
                            ? claim.trust_score >= 80 ? 'A'
                            : claim.trust_score >= 60 ? 'B'
                            : claim.trust_score >= 40 ? 'C'
                            : claim.trust_score >= 20 ? 'D' : 'F'
                            : null
                        }
                      />
                    </td>
                    <td className="px-5 py-3 text-ink-secondary">
                      {claim.submitted_at ? formatDate(claim.submitted_at) : '—'}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <span className="text-primary-700 font-medium">Review →</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}