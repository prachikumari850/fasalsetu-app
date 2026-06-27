import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/core/providers/auth_provider.dart';
import 'package:fasalsetu/features/profile/presentation/providers/profile_provider.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';
import 'package:fasalsetu/shared/widgets/app_button.dart';

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(profileProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.read(profileProvider.notifier).refresh(),
          ),
        ],
      ),
      body: profileAsync.when(
        loading: () => const LoadingWidget(),
        error: (err, _) => AppErrorWidget(
          message: err.toString(),
          onRetry: () => ref.read(profileProvider.notifier).refresh(),
        ),
        data: (user) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Center(
              child: CircleAvatar(
                radius: 40,
                backgroundColor: AppColors.primary,
                child: Text(
                  user.fullName.isNotEmpty
                      ? user.fullName[0].toUpperCase()
                      : '?',
                  style: const TextStyle(fontSize: 32, color: Colors.white),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: Text(
                user.fullName,
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ),
            Center(
              child: Container(
                margin: const EdgeInsets.only(top: 4),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  user.role.toUpperCase(),
                  style: const TextStyle(
                    color: AppColors.primary,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Card(
              child: Column(
                children: [
                  ListTile(
                    leading: const Icon(Icons.email_outlined),
                    title: const Text('Email'),
                    subtitle: Text(user.email),
                  ),
                  if (user.phone != null)
                    ListTile(
                      leading: const Icon(Icons.phone_outlined),
                      title: const Text('Phone'),
                      subtitle: Text(user.phone!),
                    ),
                  if (user.district != null)
                    ListTile(
                      leading: const Icon(Icons.location_on_outlined),
                      title: const Text('District'),
                      subtitle: Text(user.district!),
                    ),
                  ListTile(
                    leading: const Icon(Icons.public_outlined),
                    title: const Text('State'),
                    subtitle: Text(user.state),
                  ),
                  ListTile(
                    leading: const Icon(Icons.language_outlined),
                    title: const Text('Preferred Language'),
                    subtitle: Text(
                      user.preferredLang == 'hi' ? 'Hindi' : 'English',
                    ),
                  ),
                  ListTile(
                    leading: Icon(
                      user.isActive
                          ? Icons.check_circle_outline_rounded
                          : Icons.block_outlined,
                      color:
                          user.isActive ? AppColors.success : AppColors.error,
                    ),
                    title: const Text('Account Status'),
                    subtitle: Text(user.isActive ? 'Active' : 'Inactive'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            AppButton(
              label: 'Sign out',
              variant: AppButtonVariant.danger,
              icon: Icons.logout_rounded,
              onPressed: () => ref.read(authProvider.notifier).signOut(),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}