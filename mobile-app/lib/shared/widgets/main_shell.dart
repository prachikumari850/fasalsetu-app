import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/l10n/app_localizations.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';

class MainShell extends ConsumerWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  int _locationToIndex(String location) {
    if (location.startsWith('/farms')) return 1;
    if (location.startsWith('/claims')) return 2;
    if (location.startsWith('/advisories')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final location = GoRouterState.of(context).matchedLocation;
    final currentIndex = _locationToIndex(location);

    return Scaffold(
      body: child,
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(top: BorderSide(color: AppColors.border)),
        ),
        child: BottomNavigationBar(
          currentIndex: currentIndex,
          onTap: (index) {
            switch (index) {
              case 0:
                context.go('/dashboard');
                break;
              case 1:
                context.go('/farms');
                break;
              case 2:
                context.go('/claims');
                break;
              case 3:
                context.go('/advisories');
                break;
              case 4:
                context.go('/profile');
                break;
            }
          },
          items: [
            BottomNavigationBarItem(
              icon: const Icon(Icons.dashboard_outlined),
              activeIcon: const Icon(Icons.dashboard),
              label: l10n.dashboardTitle,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.agriculture_outlined),
              activeIcon: const Icon(Icons.agriculture),
              label: l10n.myFarms,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.assignment_outlined),
              activeIcon: const Icon(Icons.assignment),
              label: l10n.claims,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.tips_and_updates_outlined),
              activeIcon: const Icon(Icons.tips_and_updates),
              label: l10n.advisories,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.person_outline),
              activeIcon: const Icon(Icons.person),
              label: l10n.profile,
            ),
          ],
        ),
      ),
    );
  }
}
