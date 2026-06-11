import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/providers/auth_provider.dart';
import 'package:fasalsetu/features/auth/presentation/pages/login_page.dart';
import 'package:fasalsetu/features/auth/presentation/pages/otp_page.dart';
import 'package:fasalsetu/shared/widgets/main_shell.dart';
import 'package:fasalsetu/features/farm/presentation/pages/dashboard_page.dart';
import 'package:fasalsetu/features/farm/presentation/pages/farm_list_page.dart';
import 'package:fasalsetu/features/claims/presentation/pages/claims_page.dart';
import 'package:fasalsetu/features/advisory/presentation/pages/advisory_page.dart';
import 'package:fasalsetu/features/profile/presentation/pages/profile_page.dart';
import 'package:fasalsetu/features/farm/presentation/pages/farm_register_page.dart';
import 'package:fasalsetu/features/farm/presentation/pages/farm_detail_page.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
    debugLogDiagnostics: true,
    redirect: (context, state) {
      final isAuthenticated = authState.isAuthenticated;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');
      final isUnknown = authState.status == AuthStatus.unknown;

      if (isUnknown) return '/splash';
      if (!isAuthenticated && !isAuthRoute) return '/auth/login';
      if (isAuthenticated && isAuthRoute) return '/dashboard';
      return null;
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (_, __) => const SplashPage(),
      ),
      GoRoute(
        path: '/auth/login',
        builder: (_, __) => const LoginPage(),
      ),
      GoRoute(
        path: '/auth/otp',
        builder: (context, state) {
          final email = state.extra as String;
          return OtpPage(email: email);
        },
      ),
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (_, __) => const DashboardPage(),
          ),

          // Add these inside the ShellRoute routes list, after '/dashboard'
          GoRoute(
            path: '/farms',
            builder: (_, __) => const FarmListPage(),
          ),
          GoRoute(
            path: '/farms/register',
            // parentNavigatorKey: _rootNavigatorKey, // Full screen, no bottom nav
            builder: (_, __) => const FarmRegisterPage(),
          ),
          GoRoute(
            path: '/farms/:farmId',
            //parentNavigatorKey: _rootNavigatorKey,
            builder: (context, state) {
              final farmId = state.pathParameters['farmId']!;
              return FarmDetailPage(farmId: farmId);
            },
          ),
          GoRoute(
            path: '/claims',
            builder: (_, __) => const ClaimsPage(),
          ),
          GoRoute(
            path: '/advisories',
            builder: (_, __) => const AdvisoryPage(),
          ),
          GoRoute(
            path: '/profile',
            builder: (_, __) => const ProfilePage(),
          ),
        ],
      ),
    ],
  );
});

// Simple splash page while auth state resolves
class SplashPage extends StatelessWidget {
  const SplashPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: Color(0xFF2E7D32),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.eco, size: 64, color: Colors.white),
            SizedBox(height: 16),
            Text(
              'FasalSetu',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                fontFamily: 'NotoSansDevanagari',
              ),
            ),
            SizedBox(height: 32),
            CircularProgressIndicator(color: Colors.white54),
          ],
        ),
      ),
    );
  }
}
