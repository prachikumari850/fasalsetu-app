import { useState } from 'react';
import { PageHeader } from '../../../components/layout/PageHeader';
import { Card } from '../../../components/ui/Card';
import { Skeleton } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { useUsers } from '../../../hooks/useAdmin';
import { formatDate } from '../../../utils/format';
import { UsersIcon } from '@heroicons/react/24/outline';

const ROLE_FILTERS = [
  { label: 'All',     value: '' },
  { label: 'Farmers', value: 'farmer' },
  { label: 'Officers',value: 'officer' },
  { label: 'Admins',  value: 'admin' },
];

export function UsersPage() {
  const [roleFilter, setRoleFilter] = useState('');
  const [search, setSearch]         = useState('');
  const { data: users, isLoading }  = useUsers();

  const filtered = (users ?? []).filter(u => {
    const matchRole   = !roleFilter || u.role === roleFilter;
    const matchSearch = !search ||
      u.full_name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase());
    return matchRole && matchSearch;
  });

  return (
    <div>
      <PageHeader
        title="User Management"
        subtitle={`${users?.length ?? 0} total users`}
      />
      <div className="grid  grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">

  <Card>
    <div className="p-5">
      <p className="text-sm text-gray-500">Total Users</p>
      <h2 className="text-3xl font-bold">{users?.length ?? 0}</h2>
    </div>
  </Card>

  <Card>
    <div className="p-5">
      <p className="text-sm text-gray-500">Farmers</p>
      <h2 className="text-3xl font-bold text-green-600">
        {users?.filter(u => u.role === "farmer").length ?? 0}
      </h2>
    </div>
  </Card>

  <Card>
    <div className="p-5">
      <p className="text-sm text-gray-500">Officers</p>
      <h2 className="text-3xl font-bold text-blue-600">
        {users?.filter(u => u.role === "officer").length ?? 0}
      </h2>
    </div>
  </Card>

  <Card>
    <div className="p-5">
      <p className="text-sm text-gray-500">Admins</p>
      <h2 className="text-3xl font-bold text-purple-600">
        {users?.filter(u => u.role === "admin").length ?? 0}
      </h2>
    </div>
  </Card>

</div>

     <div className="flex flex-col sm:flex-row gap-3 mb-5">
  <input
    type="text"
    placeholder="Search users by name or email..."
    value={search}
    onChange={(e) => setSearch(e.target.value)}
    className="w-full flex-1 rounded-lg border border-border bg-surface px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-700"
  />

  <div className="flex gap-2 flex-wrap">
    {ROLE_FILTERS.map((f) => (
      <button
        key={f.value}
        onClick={() => setRoleFilter(f.value)}
        className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
          roleFilter === f.value
            ? "bg-primary-700 text-white"
            : "bg-surface border border-border text-ink-secondary hover:bg-muted"
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
            {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-14 rounded-lg" />)}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            title="No users found"
            description="No users match the selected filters."
            icon={<UsersIcon className="h-12 w-12" />}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted">
                  <th className="text-left px-5 py-3 label">Name</th>
                  <th className="text-left px-5 py-3 label">Email</th>
                  <th className="text-left px-5 py-3 label">Role</th>
                  <th className="text-left px-5 py-3 label">District</th>
                  <th className="text-left px-5 py-3 label">Language</th>
                  <th className="text-left px-5 py-3 label">Joined</th>
                  <th className="text-left px-5 py-3 label">Status</th>
                  <th className="text-center px-5 py-3 label">Actions</th>
 
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map(user => (
                  <tr key={user.id} className="hover:bg-muted transition-colors">
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-3">
                        <div className="h-7 w-7 rounded-full bg-primary-100
                                        text-primary-700 flex items-center justify-center
                                        text-xs font-bold flex-shrink-0">
                          {user.full_name
  .split(" ")
  .map(name => name[0])
  .join("")
  .slice(0, 2)
  .toUpperCase()}
                        </div>
                        <span className="font-medium text-ink">{user.full_name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-ink-secondary">{user.email}</td>
                    <td className="px-5 py-3">
                      <span className={`text-xs font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full
                        ${user.role === 'admin'   ? 'bg-purple-100 text-purple-700'
                        : user.role === 'officer' ? 'bg-blue-100   text-blue-700'
                        :                          'bg-green-100  text-green-700'}`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-ink-secondary">
                      {user.district ?? '—'}
                    </td>
                    <td className="px-5 py-3 text-ink-secondary capitalize">
                      {user.preferred_lang === 'hi' ? 'Hindi' : 'English'}
                    </td>
                    <td className="px-5 py-3 text-ink-secondary">
                      {formatDate(user.created_at)}
                    </td>
                    <td className="px-5 py-3">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full
                        ${user.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100   text-red-700'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    


<td className="px-5 py-3">
  <div className="flex justify-center gap-2">

    <button className="min-w-[80px] rounded-lg bg-blue-600 px-3 py-2 text-xs font-medium text-white">
  View
</button>

    <button className="min-w-[80px] rounded-lg bg-yellow-500 px-3 py-2 text-xs font-medium text-white">
      Edit
    </button>

    <button
      className={`min-w-[95px] rounded-lg px-3 py-2 text-xs font-medium text-white ${
  user.is_active
    ? "bg-red-600"
    : "bg-green-600"
}`}
    >
      {user.is_active ? "Deactivate" : "Activate"}
    </button>

  </div>
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