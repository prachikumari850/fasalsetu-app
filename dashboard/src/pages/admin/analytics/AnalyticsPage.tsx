import { PageHeader } from '../../../components/layout/PageHeader';
import { Card, CardHeader } from '../../../components/ui/Card';
import { Skeleton } from '../../../components/ui/Skeleton';
import { useAdminStats } from '../../../hooks/useAdmin';

export function AnalyticsPage() {
  const { data: stats, isLoading } = useAdminStats();

  return (
    <div>
      <PageHeader
        title="Analytics"
        subtitle="Platform-wide statistics and trends"
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* Claims Analytics */}
        <Card>
          <CardHeader title="Claims Overview" />
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-8 rounded-lg" />)}
            </div>
          ) : stats ? (
            <div className="space-y-4">
              {[
                { label: 'Total Claims',        value: stats.total_claims,    pct: 100 },
                { label: 'Approved',            value: stats.approved_claims,
                  pct: stats.total_claims > 0 ? (stats.approved_claims / stats.total_claims) * 100 : 0 },
                { label: 'Pending Review',      value: stats.pending_claims,
                  pct: stats.total_claims > 0 ? (stats.pending_claims / stats.total_claims) * 100 : 0 },
                { label: 'Rejected',            value: stats.rejected_claims,
                  pct: stats.total_claims > 0 ? (stats.rejected_claims / stats.total_claims) * 100 : 0 },
              ].map(item => (
                <div key={item.label} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-ink">{item.label}</span>
                    <span className="font-semibold">{item.value}</span>
                  </div>
                  <div className="h-2 bg-border rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-600 rounded-full transition-all duration-500"
                      style={{ width: `${item.pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-ink-secondary">No data available.</p>
          )}
        </Card>

        {/* Platform stats */}
        <Card>
          <CardHeader title="Platform Overview" />
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-10 rounded-lg" />)}
            </div>
          ) : stats ? (
            <div className="divide-y divide-border">
              {[
                { label: 'Registered Farmers',  value: stats.total_farmers },
                { label: 'Registered Farms',    value: stats.total_farms },
                { label: 'Average Trust Score', value: stats.avg_trust_score?.toFixed(1) ?? '—' },
                { label: 'Approval Rate',
                  value: stats.total_claims > 0
                    ? `${((stats.approved_claims / stats.total_claims) * 100).toFixed(1)}%`
                    : '—' },
              ].map(item => (
                <div key={item.label}
                  className="flex items-center justify-between py-3 text-sm">
                  <span className="text-ink-secondary">{item.label}</span>
                  <span className="font-semibold text-ink">{item.value}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-ink-secondary">No data available.</p>
          )}
        </Card>
      </div>
    </div>
  );
}