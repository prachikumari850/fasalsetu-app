import { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '../components/layout/Sidebar';
import { Navbar } from '../components/layout/Navbar';
import { useIsMobile } from '../hooks/useMediaQuery';
import { cn } from '../utils/cn';

const routeTitles: Record<string, string> = {
  '/officer':          'Officer Dashboard',
  '/officer/claims':   'Claims Management',
  '/officer/fraud':    'Fraud Detection',
  '/admin':            'Admin Dashboard',
  '/admin/analytics':  'Analytics',
  '/admin/users':      'User Management',
  '/admin/settings':   'Settings',
};

export function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const isMobile = useIsMobile();
  const location = useLocation();
  const title = routeTitles[location.pathname] ?? 'FasalSetu';

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  return (
    <div className="flex h-screen overflow-hidden bg-muted">
      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <Sidebar />
      </div>

      {/* Mobile sidebar overlay */}
      {isMobile && (
        <>
          {/* Backdrop */}
          <div
            className={cn(
              'fixed inset-0 z-40 bg-black/40 transition-opacity lg:hidden',
              sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
            )}
            onClick={() => setSidebarOpen(false)}
          />
          {/* Drawer */}
          <div
            className={cn(
              'fixed inset-y-0 left-0 z-50 transition-transform lg:hidden',
              sidebarOpen ? 'translate-x-0' : '-translate-x-full'
            )}
          >
            <Sidebar onClose={() => setSidebarOpen(false)} />
          </div>
        </>
      )}

      {/* Main */}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        <Navbar
          title={title}
          onMenuClick={() => setSidebarOpen(true)}
        />
        <main className="flex-1 overflow-y-auto">
          <div className="page-container">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}