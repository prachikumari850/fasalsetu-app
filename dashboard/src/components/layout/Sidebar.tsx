import { NavLink, useNavigate } from 'react-router-dom';
import {
  HomeIcon, ClipboardDocumentListIcon, ShieldExclamationIcon,
  UsersIcon, ChartBarIcon, Cog6ToothIcon, ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid, ClipboardDocumentListIcon as ClipDocSolid,
  ShieldExclamationIcon as ShieldSolid, UsersIcon as UsersSolid,
  ChartBarIcon as ChartSolid, Cog6ToothIcon as CogSolid,
} from '@heroicons/react/24/solid';
import { cn } from '../../utils/cn';
import { useAuth } from '../../hooks/useAuth';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  activeIcon: React.ReactNode;
  roles: ('officer' | 'admin')[];
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/officer',
    icon: <HomeIcon className="h-5 w-5" />,
    activeIcon: <HomeIconSolid className="h-5 w-5" />,
    roles: ['officer'],
  },
  {
    label: 'Claims',
    href: '/officer/claims',
    icon: <ClipboardDocumentListIcon className="h-5 w-5" />,
    activeIcon: <ClipDocSolid className="h-5 w-5" />,
    roles: ['officer'],
  },
  {
    label: 'Fraud Detection',
    href: '/officer/fraud',
    icon: <ShieldExclamationIcon className="h-5 w-5" />,
    activeIcon: <ShieldSolid className="h-5 w-5" />,
    roles: ['officer'],
  },
  {
    label: 'Dashboard',
    href: '/admin',
    icon: <HomeIcon className="h-5 w-5" />,
    activeIcon: <HomeIconSolid className="h-5 w-5" />,
    roles: ['admin'],
  },
  {
    label: 'Analytics',
    href: '/admin/analytics',
    icon: <ChartBarIcon className="h-5 w-5" />,
    activeIcon: <ChartSolid className="h-5 w-5" />,
    roles: ['admin'],
  },
  {
    label: 'Users',
    href: '/admin/users',
    icon: <UsersIcon className="h-5 w-5" />,
    activeIcon: <UsersSolid className="h-5 w-5" />,
    roles: ['admin'],
  },
  {
    label: 'Settings',
    href: '/admin/settings',
    icon: <Cog6ToothIcon className="h-5 w-5" />,
    activeIcon: <CogSolid className="h-5 w-5" />,
    roles: ['admin'],
  },
];

interface SidebarProps {
  onClose?: () => void;
}

export function Sidebar({ onClose }: SidebarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const visibleItems = navItems.filter((item) =>
    user ? item.roles.includes(user.role as 'officer' | 'admin') : false
  );

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="flex flex-col h-full bg-surface border-r border-border w-64">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-border flex-shrink-0">
        <div className="h-8 w-8 bg-primary-700 rounded-xl flex items-center justify-center">
          <span className="text-white font-bold text-sm">FS</span>
        </div>
        <div>
          <p className="font-bold text-sm text-ink">FasalSetu</p>
          <p className="text-xs text-ink-hint capitalize">{user?.role} Portal</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        {visibleItems.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            end={item.href === '/officer' || item.href === '/admin'}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-ink-secondary hover:bg-muted hover:text-ink'
              )
            }
          >
            {({ isActive }) => (
              <>
                <span>{isActive ? item.activeIcon : item.icon}</span>
                {item.label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User + Logout */}
      <div className="border-t border-border p-3 flex-shrink-0 space-y-1">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-muted">
          <div className="h-8 w-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-bold flex-shrink-0">
            {user?.full_name.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-ink truncate">{user?.full_name}</p>
            <p className="text-xs text-ink-hint truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-ink-secondary hover:bg-red-50 hover:text-danger transition-colors"
        >
          <ArrowRightOnRectangleIcon className="h-5 w-5" />
          Logout
        </button>
      </div>
    </aside>
  );
}