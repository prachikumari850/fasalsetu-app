import { useNavigate } from 'react-router-dom';
import {
  UsersIcon, BuildingOfficeIcon,
  ClipboardDocumentListIcon, ShieldCheckIcon,
} from '@heroicons/react/24/outline';
import { PageHeader } from '../../components/layout/PageHeader';
import { StatCard } from '../../components/charts/StatCard';
import { Card, CardHeader } from '../../components/ui/Card';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAdminStats, useUsers } from '../../hooks/useAdmin';
import { formatDate } from '../../utils/format';

export function AdminDashboard() {
  const { data: stats, isLoading } = useAdminStats();
  const { data: users }            = useUsers();
  const navigate                   = useNavigate();

  const recentUsers = (users ?? []).slice(0, 6);

  return (
    <div>
      <PageHeader
        title="Admin Dashboard"
        subtitle="Platform overview and analytics"
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="Total Farmers"
          value={stats?.total_farmers ?? 0}
          icon={<UsersIcon className="h-5 w-5" />}
          color="green"
          isLoading={isLoading}
        />
        <StatCard
          title="Registered Farms"
          value={stats?.total_farms ?? 0}
          icon={<BuildingOfficeIcon className="h-5 w-5" />}
          color="blue"
          isLoading={isLoading}
        />
        <StatCard
          title="Total Claims"
          value={stats?.total_claims ?? 0}
          icon={<ClipboardDocumentListIcon className="h-5 w-5" />}
          color="orange"
          isLoading={isLoading}
        />
        <StatCard
          title="Avg Trust Score"
          value={stats?.avg_trust_score ? `${stats.avg_trust_score.toFixed(0)}` : '—'}
          icon={<ShieldCheckIcon className="h-5 w-5" />}
          color="green"
          isLoading={isLoading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* Claims breakdown */}
        <Card>
          <CardHeader title="Claims by Status" />
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-10 rounded-lg" />)}
            </div>
          ) : stats ? (
            <div className="space-y-3">
              {[
                { label: 'Pending Review',    value: stats.pending_claims,  color: 'bg-amber-400' },
                { label: 'Approved',          value: stats.approved_claims, color: 'bg-green-500' },
                { label: 'Rejected',          value: stats.rejected_claims, color: 'bg-red-500' },
              ].map(item => (
                <div key={item.label} className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full flex-shrink-0"
                       style={{ backgroundColor: item.color.replace('bg-', '') }} />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-ink">{item.label}</span>
                      <span className="font-medium">{item.value}</span>
                    </div>
                    <div className="h-1.5 bg-border rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${item.color}`}
                        style={{
                          width: stats.total_claims > 0
                            ? `${(item.value / stats.total_claims) * 100}%`
                            : '0%',
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-ink-secondary">No data yet.</p>
          )}
        </Card>

        {/* Recent users */}
        <Card>
          <CardHeader
            title="Recent Users"
            action={
              <button
                onClick={() => navigate('/admin/users')}
                className="text-sm text-primary-700 font-medium hover:underline"
              >
                View all →
              </button>
            }
          />
          {!users ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-10 rounded-lg" />)}
            </div>
          ) : (
            <div className="space-y-2">
              {recentUsers.map(user => (
                <div key={user.id}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted">
                  <div className="h-8 w-8 rounded-full bg-primary-100 text-primary-700
                                  flex items-center justify-center text-xs font-bold flex-shrink-0">
                    {user.full_name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-ink truncate">{user.full_name}</p>
                    <p className="text-xs text-ink-hint truncate">{user.email}</p>
                  </div>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full
                    ${user.role === 'admin'   ? 'bg-purple-100 text-purple-700'
                    : user.role === 'officer' ? 'bg-blue-100 text-blue-700'
                    :                          'bg-green-100 text-green-700'}`}>
                    {user.role}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}