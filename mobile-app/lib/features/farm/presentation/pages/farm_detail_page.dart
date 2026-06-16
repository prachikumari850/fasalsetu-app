import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/shared/widgets/app_button.dart';

class FarmDetailPage extends ConsumerWidget {
  final String farmId;
  const FarmDetailPage({super.key, required this.farmId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Farm Detail'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => context.pop(),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            AppButton(
              label: 'View Crop Lifecycle',
              onPressed: () => context.push(
                '/farms/$farmId/lifecycle',
                extra: 'My Farm',
              ),
              icon: Icons.timeline_rounded,
            ),
          ],
        ),
      ),
    );
  }
}
