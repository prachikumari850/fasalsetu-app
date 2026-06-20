import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../../components/layout/PageHeader';
import { Card } from '../../../components/ui/Card';
import { StatusBadge } from '../../../components/ui/StatusBadge';
import { TrustScoreBadge } from '../../../components/ui/TrustScoreBadge';
import { Skeleton } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { useClaims } from '../../../hooks/useClaims';
import { formatDate } from '../../../utils/format';
import { ClipboardDocumentListIcon } from '@heroicons/react/24/outline';

const STATUS_FILTERS = [
  { label: 'All',              value: '' },
  { label: 'Pending',          value: 'submitted' },
  { label: 'Under Review',     value: 'under_review' },
  { label: 'Needs Inspection', value: 'needs_inspection' },
  { label: 'Approved',         value: 'approved' },
  { label: 'Rejected',         value: 'rejected' },
];

export function ClaimsListPage() {
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch]             = useState('');
  const { data: claims, isLoading }     = useClaims();
  const navigate                        = useNavigate();

  const filtered = (claims ?? []).filter(c => {
    const matchStatus = !statusFilter || c.status === statusFilter;
    const matchSearch = !search ||
      c.id.toLowerCase().includes(search.toLowerCase()) ||
      c.damage_type.toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  return (
    <div>
      <PageHeader
        title="Claims Management"
        subtitle={`${claims?.length ?? 0} total claims`}
      />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <input
          type="text"
          placeholder="Search by claim ID or damage type..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1 rounded-lg border border-border bg-surface px-3 py-2
                     text-sm focus:outline-none focus:ring-2 focus:ring-primary-700"
        />
        <div className="flex gap-2 flex-wrap">
          {STATUS_FILTERS.map(f => (
            <button
              key={f.value}
              onClick={() => setStatusFilter(f.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                ${statusFilter === f.value
                  ? 'bg-primary-700 text-white'
                  : 'bg-surface border border-border text-ink-secondary hover:bg-muted'
                }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <Card padding={false}>
        {isLoading ? (
          <div className="p-4 space-y-3">
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} className="h-14 rounded-lg" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            title="No claims found"
            description="Try adjusting your filters."
            icon={<ClipboardDocumentListIcon className="h-12 w-12" />}
          />
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
                {filtered.map(claim => (
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
                    <td className="px-5 py-3 text-right text-primary-700 font-medium">
                      Review →
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