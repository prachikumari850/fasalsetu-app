// lib/core/router/app_router.dart
// Added missing routes:
//   /claims/new      → NewClaimPage
//   /claims/:claimId → ClaimDetailPage
// All other routes unchanged from original.

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/providers/auth_provider.dart';
import 'package:fasalsetu/features/auth/presentation/pages/login_page.dart';
import 'package:fasalsetu/features/auth/presentation/pages/otp_page.dart';
import 'package:fasalsetu/shared/widgets/main_shell.dart';
import 'package:fasalsetu/features/farm/presentation/pages/dashboard_page.dart';
import 'package:fasalsetu/features/farm/presentation/pages/farm_list_page.dart';
import 'package:fasalsetu/features/farm/presentation/pages/farm_register_page.dart';
import 'package:fasalsetu/features/farm/presentation/pages/farm_detail_page.dart';
import 'package:fasalsetu/features/crop/presentation/pages/crop_lifecycle_page.dart';
import 'package:fasalsetu/features/claims/presentation/pages/claims_page.dart';
import 'package:fasalsetu/features/claims/presentation/pages/claim_detail_page.dart';
import 'package:fasalsetu/features/advisory/presentation/pages/advisory_page.dart';
import 'package:fasalsetu/features/profile/presentation/pages/profile_page.dart';
import 'package:fasalsetu/features/health/presentation/pages/crop_health_page.dart';
import 'package:fasalsetu/features/analysis/presentation/pages/image_analysis_page.dart';

final _rootNavigatorKey  = GlobalKey<NavigatorState>(debugLabel: 'root');
final _shellNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'shell');

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
    // GoRouter diagnostics print full locations, including query parameters.
    // Keep them off so signed storage URLs can never reach browser logs.
    debugLogDiagnostics: false,
    redirect: (context, state) {
      final status         = authState.status;
      final isAuthenticated = authState.isAuthenticated;
      final loc            = state.matchedLocation;
      final isAuthRoute    = loc.startsWith('/auth');
      final isSplash       = loc == '/splash';

      if (status == AuthStatus.unknown) return isSplash ? null : '/splash';
      if (isAuthenticated && (isAuthRoute || isSplash)) return '/dashboard';
      if (!isAuthenticated && (isSplash || !isAuthRoute)) return '/auth/login';

      return null;
    },
    routes: [
      // ── Splash ────────────────────────────────────────────────────────
      GoRoute(
        path: '/splash',
        builder: (_, __) => const SplashPage(),
      ),

      // ── Auth ──────────────────────────────────────────────────────────
      GoRoute(
        path: '/auth/login',
        builder: (_, __) => const LoginPage(),
      ),
      GoRoute(
        path: '/auth/otp',
        builder: (context, state) {
          final email = state.uri.queryParameters['email'] ?? '';
          return OtpPage(email: email);
        },
      ),

      // ── Full-screen (no bottom nav) ────────────────────────────────────
      GoRoute(
        path: '/farms/register',
        builder: (_, __) => const FarmRegisterPage(),
      ),
      GoRoute(
        path: '/farms/:farmId',
        builder: (context, state) {
          final farmId = state.pathParameters['farmId']!;
          return FarmDetailPage(farmId: farmId);
        },
      ),
      GoRoute(
        path: '/farms/:farmId/lifecycle',
        builder: (context, state) {
          final farmId   = state.pathParameters['farmId']!;
          final farmName = state.uri.queryParameters['name'] ?? 'Farm';
          return CropLifecyclePage(farmId: farmId, farmName: farmName);
        },
      ),
      GoRoute(
        path: '/farms/:farmId/health',
        builder: (context, state) {
          final farmId   = state.pathParameters['farmId']!;
          final farmName = state.uri.queryParameters['name'] ?? 'Farm';
          return CropHealthPage(farmId: farmId, farmName: farmName);
        },
      ),
      GoRoute(
        path: '/farms/:farmId/analysis/:imageId',
        builder: (context, state) {
          final farmId   = state.pathParameters['farmId']!;
          final imageId  = state.pathParameters['imageId']!;
          return ImageAnalysisPage(farmId: farmId, imageId: imageId);
        },
      ),

      // ── Claims full-screen (outside shell so bottom nav hidden) ───────
      GoRoute(
        path: '/claims/new',
        builder: (_, __) => const NewClaimPage(),
      ),
      GoRoute(
        path: '/claims/:claimId',
        builder: (context, state) {
          final claimId = state.pathParameters['claimId']!;
          return ClaimDetailPage(claimId: claimId);
        },
      ),

      // ── Shell (bottom nav visible) ────────────────────────────────────
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (_, __) => const DashboardPage(),
          ),
          GoRoute(
            path: '/farms',
            builder: (_, __) => const FarmListPage(),
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

// ── Splash ────────────────────────────────────────────────────────────────────
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
