import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/shared/widgets/app_button.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';
import 'package:fasalsetu/features/farm/presentation/providers/farm_detail_provider.dart';
import 'package:fasalsetu/features/farm/domain/entities/farm_entity.dart';
import 'package:fasalsetu/features/trust/presentation/providers/trust_provider.dart';
import 'package:fasalsetu/features/trust/presentation/widgets/trust_score_widget.dart';

class FarmDetailPage extends ConsumerWidget {
  final String farmId;
  const FarmDetailPage({super.key, required this.farmId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final farmAsync = ref.watch(farmDetailProvider(farmId));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Farm Detail'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.invalidate(farmDetailProvider(farmId)),
          ),
        ],
      ),
      body: farmAsync.when(
        loading: () => const LoadingWidget(),
        error: (e, _) => AppErrorWidget(
          message: e.toString(),
          onRetry: () => ref.invalidate(farmDetailProvider(farmId)),
        ),
        data: (farm) => _FarmDetailBody(farm: farm, ref: ref),
      ),
    );
  }
}

class _FarmDetailBody extends StatelessWidget {
  final FarmEntity farm;
  final WidgetRef ref;

  const _FarmDetailBody({required this.farm, required this.ref});

  @override
  Widget build(BuildContext context) {
    final trustAsync = ref.watch(trustScoreProvider(farm.id));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: const Icon(
                      Icons.agriculture_rounded,
                      color: AppColors.primary,
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          farm.name,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${farm.village}, ${farm.district}',
                          style: const TextStyle(
                            fontSize: 13,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (!farm.isActive)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.warning.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text(
                        'Inactive',
                        style: TextStyle(
                          color: AppColors.warning,
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Trust score
          trustAsync.when(
            loading: () => const SizedBox(
              height: 88,
              child: Center(
                child: CircularProgressIndicator(
                  color: AppColors.primary,
                  strokeWidth: 2,
                ),
              ),
            ),
            error: (_, __) => const SizedBox.shrink(),
            data: (trust) => Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: TrustScoreCard(trust: trust),
            ),
          ),

          // Farm info grid
          const Text(
            'Farm Information',
            style: TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
          ),
          const SizedBox(height: 10),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(4),
              child: Column(
                children: [
                  _InfoRow(
                    icon: Icons.eco_outlined,
                    label: 'Crop Type',
                    value: farm.cropType,
                  ),
                  _InfoRow(
                    icon: Icons.calendar_today_outlined,
                    label: 'Season',
                    value: farm.season,
                  ),
                  _InfoRow(
                    icon: Icons.straighten_rounded,
                    label: 'Area',
                    value: '${farm.areaAcres} acres',
                  ),
                  if (farm.taluka != null)
                    _InfoRow(
                      icon: Icons.location_city_outlined,
                      label: 'Taluka',
                      value: farm.taluka!,
                    ),
                  _InfoRow(
                    icon: Icons.map_outlined,
                    label: 'State',
                    value: farm.state,
                  ),
                  if (farm.khasraNumber != null)
                    _InfoRow(
                      icon: Icons.numbers_rounded,
                      label: 'Khasra Number',
                      value: farm.khasraNumber!,
                    ),
                  _InfoRow(
                    icon: farm.boundary != null
                        ? Icons.check_circle_outline_rounded
                        : Icons.location_off_outlined,
                    label: 'GPS Boundary',
                    value: farm.boundary != null ? 'Mapped' : 'Not mapped',
                    valueColor: farm.boundary != null
                        ? AppColors.success
                        : AppColors.textHint,
                    isLast: true,
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          AppButton(
            label: 'View Crop Lifecycle',
            icon: Icons.timeline_rounded,
            onPressed: () => context.push(
              '/farms/${farm.id}/lifecycle',
              extra: farm.name,
            ),
          ),

          const SizedBox(height: 12),

          AppButton(
            label: 'View Crop Health',
            icon: Icons.health_and_safety_outlined,
            variant: AppButtonVariant.outlined,
            onPressed: () => context.push(
              '/farms/${farm.id}/health?name=${Uri.encodeComponent(farm.name)}',
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color? valueColor;
  final bool isLast;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
    this.valueColor,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      decoration: BoxDecoration(
        border: isLast
            ? null
            : const Border(
                bottom: BorderSide(color: AppColors.border, width: 0.6),
              ),
      ),
      child: Row(
        children: [
          Icon(icon, size: 18, color: AppColors.textSecondary),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 13,
                color: AppColors.textSecondary,
              ),
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }
}