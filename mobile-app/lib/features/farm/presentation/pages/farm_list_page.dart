import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fasalsetu/l10n/app_localizations.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/core/providers/auth_provider.dart';
import 'package:fasalsetu/features/farm/domain/entities/farm_entity.dart';
import 'package:fasalsetu/features/farm/presentation/providers/farm_provider.dart';
import 'package:fasalsetu/shared/widgets/app_button.dart';
import 'package:fasalsetu/shared/widgets/empty_state_widget.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';

class FarmListPage extends ConsumerWidget {
  const FarmListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final user = ref.watch(authProvider).user;
    final farmsAsync = ref.watch(myFarmsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(l10n.myFarms),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.read(myFarmsProvider.notifier).refresh(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/farms/register'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add_rounded),
        label: Text(l10n.addFarm),
      ),
      body: RefreshIndicator(
        color: AppColors.primary,
        onRefresh: () => ref.read(myFarmsProvider.notifier).refresh(),
        child: farmsAsync.when(
          loading: () => const LoadingWidget(),
          error: (e, _) => AppErrorWidget(
            message: e.toString(),
            onRetry: () => ref.read(myFarmsProvider.notifier).refresh(),
          ),
          data: (farms) {
            if (farms.isEmpty) {
              return SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: SizedBox(
                  height: MediaQuery.sizeOf(context).height * 0.7,
                  child: EmptyStateWidget(
                    icon: Icons.agriculture_outlined,
                    message: l10n.noFarms,
                    subMessage: l10n.registerFarm,
                    action: AppButton(
                      label: l10n.addFarm,
                      onPressed: () => context.push('/farms/register'),
                      fullWidth: false,
                      icon: Icons.add_rounded,
                    ),
                  ),
                ),
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
              itemCount: farms.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) => _FarmCard(
                farm: farms[index],
                onTap: () => context.push('/farms/${farms[index].id}'),
                onDelete: () => _confirmDelete(
                  context,
                  ref,
                  l10n,
                  farms[index],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Future<void> _confirmDelete(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    FarmEntity farm,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Text(l10n.farmName),
        content: Text('Delete "${farm.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(l10n.cancel),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.error),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await ref.read(myFarmsProvider.notifier).removeFarm(farm.id);
    }
  }
}

class _FarmCard extends StatelessWidget {
  final FarmEntity farm;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const _FarmCard({
    required this.farm,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row
              Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.agriculture_rounded,
                      color: AppColors.primary,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          farm.name,
                          style: Theme.of(context).textTheme.titleLarge,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${farm.village}, ${farm.district}',
                          style: Theme.of(context).textTheme.bodyMedium,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  PopupMenuButton<String>(
                    onSelected: (value) {
                      if (value == 'delete') onDelete();
                    },
                    itemBuilder: (_) => [
                      const PopupMenuItem(
                        value: 'delete',
                        child: Row(
                          children: [
                            Icon(Icons.delete_outline,
                                color: AppColors.error, size: 18),
                            SizedBox(width: 8),
                            Text('Delete',
                                style: TextStyle(color: AppColors.error)),
                          ],
                        ),
                      ),
                    ],
                    child:
                        const Icon(Icons.more_vert, color: AppColors.textHint),
                  ),
                ],
              ),

              const SizedBox(height: 12),
              const Divider(height: 1),
              const SizedBox(height: 12),

              // Info chips
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _InfoChip(
                    icon: Icons.grass_rounded,
                    label: farm.cropType,
                    color: AppColors.success,
                  ),
                  _InfoChip(
                    icon: Icons.straighten_rounded,
                    label: '${farm.areaAcres.toStringAsFixed(1)} acres',
                    color: AppColors.info,
                  ),
                  _InfoChip(
                    icon: Icons.calendar_today_rounded,
                    label: farm.season,
                    color: AppColors.warning,
                  ),
                  if (farm.boundary != null)
                    _InfoChip(
                      icon: Icons.location_on_rounded,
                      label: 'GPS ✓',
                      color: AppColors.primary,
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _InfoChip({
    required this.icon,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: color,
              fontFamily: 'NotoSansDevanagari',
            ),
          ),
        ],
      ),
    );
  }
}
