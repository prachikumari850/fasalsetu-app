import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { RoleGuard } from './RoleGuard';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { AuthLayout } from '../layouts/AuthLayout';
import { LoginPage } from '../pages/auth/LoginPage';
import { OfficerDashboard } from '../pages/officer/OfficerDashboard';
import { ClaimsListPage } from '../pages/officer/claims/ClaimsListPage';
import { ClaimDetailPage } from '../pages/officer/claims/ClaimDetailPage';
import { FraudDashboardPage } from '../pages/officer/fraud/FraudDashboardPage';
import { AdminDashboard } from '../pages/admin/AdminDashboard';
import { AnalyticsPage } from '../pages/admin/analytics/AnalyticsPage';
import { UsersPage } from '../pages/admin/users/UsersPage';
import { SettingsPage } from '../pages/admin/settings/SettingsPage';
import { UnauthorizedPage } from '../pages/UnauthorizedPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AuthLayout />,
    children: [
      { index: true, element: <LoginPage /> },
      { path: 'login', element: <LoginPage /> },
    ],
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      // Officer routes
      {
        path: 'officer',
        element: <RoleGuard allowedRoles={['officer', 'admin']}><OfficerDashboard /></RoleGuard>,
      },
      {
        path: 'officer/claims',
        element: <RoleGuard allowedRoles={['officer', 'admin']}><ClaimsListPage /></RoleGuard>,
      },
      {
        path: 'officer/claims/:claimId',
        element: <RoleGuard allowedRoles={['officer', 'admin']}><ClaimDetailPage /></RoleGuard>,
      },
      {
        path: 'officer/fraud',
        element: <RoleGuard allowedRoles={['officer', 'admin']}><FraudDashboardPage /></RoleGuard>,
      },
      // Admin routes
      {
        path: 'admin',
        element: <RoleGuard allowedRoles={['admin']}><AdminDashboard /></RoleGuard>,
      },
      {
        path: 'admin/analytics',
        element: <RoleGuard allowedRoles={['admin']}><AnalyticsPage /></RoleGuard>,
      },
      {
        path: 'admin/users',
        element: <RoleGuard allowedRoles={['admin']}><UsersPage /></RoleGuard>,
      },
      {
        path: 'admin/settings',
        element: <RoleGuard allowedRoles={['admin']}><SettingsPage /></RoleGuard>,
      },
    ],
  },
  { path: '/unauthorized', element: <UnauthorizedPage /> },
  { path: '*', element: <NotFoundPage /> },
]);