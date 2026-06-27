import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/health/presentation/providers/health_provider.dart';
import 'package:fasalsetu/features/health/domain/entities/health_entities.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';
import 'package:fasalsetu/shared/widgets/empty_state_widget.dart';

class CropHealthPage extends ConsumerWidget {
  final String farmId;
  final String farmName;

  const CropHealthPage({
    super.key,
    required this.farmId,
    required this.farmName,
  });

  Color _healthColor(String? healthClass) {
    switch (healthClass) {
      case 'healthy':
        return AppColors.success;
      case 'mild_stress':
        return AppColors.warning;
      case 'moderate_stress':
        return AppColors.secondaryDark;
      case 'severe_stress':
        return AppColors.error;
      default:
        return AppColors.textHint;
    }
  }

  String _healthLabel(String? healthClass) {
    switch (healthClass) {
      case 'healthy':
        return 'Healthy';
      case 'mild_stress':
        return 'Mild Stress';
      case 'moderate_stress':
        return 'Moderate Stress';
      case 'severe_stress':
        return 'Severe Stress';
      default:
        return 'Unknown';
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthAsync = ref.watch(cropHealthProvider(farmId));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Crop Health'),
            Text(
              farmName,
              style: const TextStyle(fontSize: 12, color: Colors.white70),
            ),
          ],
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.invalidate(cropHealthProvider(farmId)),
          ),
        ],
      ),
      body: RefreshIndicator(
        color: AppColors.primary,
        onRefresh: () async => ref.invalidate(cropHealthProvider(farmId)),
        child: healthAsync.when(
          loading: () => const LoadingWidget(),
          error: (e, _) => AppErrorWidget(
            message: e.toString(),
            onRetry: () => ref.invalidate(cropHealthProvider(farmId)),
          ),
          data: (health) {
            if (!health.hasData) {
              return SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: SizedBox(
                  height: MediaQuery.of(context).size.height * 0.7,
                  child: EmptyStateWidget(
                    icon: Icons.health_and_safety_outlined,
                    message: 'No health data yet',
                    subMessage: health.message ??
                        'Upload crop photos to get an AI health score.',
                  ),
                ),
              );
            }
            return _HealthBody(
              health: health,
              healthColor: _healthColor(health.healthClass),
              healthLabel: _healthLabel(health.healthClass),
            );
          },
        ),
      ),
    );
  }
}

class _HealthBody extends StatelessWidget {
  final CropHealthEntity health;
  final Color healthColor;
  final String healthLabel;

  const _HealthBody({
    required this.health,
    required this.healthColor,
    required this.healthLabel,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Score banner
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: healthColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: healthColor.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: healthColor.withValues(alpha: 0.15),
                    border: Border.all(color: healthColor, width: 2),
                  ),
                  child: Center(
                    child: Text(
                      '${health.healthScore}',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: healthColor,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        healthLabel,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: healthColor,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${health.analyzedImages} of ${health.totalImages} photos analyzed',
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      if (health.lastAnalyzed != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 2),
                          child: Text(
                            'Last analyzed: ${health.lastAnalyzed!.split("T").first}',
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppColors.textHint,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          if (health.diseaseSummary.isNotEmpty) ...[
            const Text(
              'Disease Distribution',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
            ),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  children: health.diseaseSummary.entries.map((entry) {
                    final total = health.diseaseSummary.values
                        .fold<int>(0, (sum, v) => sum + (v as int));
                    final pct =
                        total > 0 ? (entry.value as int) / total : 0.0;
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment:
                                MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                entry.key
                                    .replaceAll('_', ' ')
                                    .toUpperCase(),
                                style: const TextStyle(fontSize: 12),
                              ),
                              Text(
                                '${entry.value}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(4),
                            child: LinearProgressIndicator(
                              value: pct,
                              backgroundColor: AppColors.surfaceVariant,
                              color: AppColors.warning,
                              minHeight: 6,
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),
          ] else
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  'No diseases detected in analyzed photos.',
                  style: TextStyle(color: AppColors.success),
                ),
              ),
            ),
        ],
      ),
    );
  }
}