import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Spinner } from '../components/ui/Spinner';

export function AuthLayout() {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isAuthenticated) {
    const redirect = user?.role === 'admin' ? '/admin' : '/officer';
    return <Navigate to={redirect} replace />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-700 via-primary-800 to-primary-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Brand header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-14 w-14 bg-white/20 rounded-2xl mb-4">
            <span className="text-white font-bold text-xl">FS</span>
          </div>
          <h1 className="text-2xl font-bold text-white">FasalSetu</h1>
          <p className="text-primary-200 text-sm mt-1">Smart Farming, Secure Future</p>
        </div>
        {/* Auth card */}
        <div className="bg-surface rounded-2xl shadow-modal overflow-hidden">
          <Outlet />
        </div>
      </div>
    </div>
  );
}