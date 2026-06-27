import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/advisory/presentation/providers/advisory_provider.dart';
import 'package:fasalsetu/features/advisory/domain/entities/advisory_entities.dart';
import 'package:fasalsetu/features/farm/presentation/providers/farm_provider.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';
import 'package:fasalsetu/shared/widgets/empty_state_widget.dart';

Color advisoryPriorityColor(String priority) {
  switch (priority) {
    case 'urgent':
      return AppColors.priorityUrgent;
    case 'high':
      return AppColors.priorityHigh;
    case 'medium':
      return AppColors.priorityMedium;
    default:
      return AppColors.priorityLow;
  }
}

// Local toggle: true = show Hindi text, false = show English text.
final _showHindiProvider = StateProvider<bool>((ref) => false);

class AdvisoryPage extends ConsumerStatefulWidget {
  const AdvisoryPage({super.key});

  @override
  ConsumerState<AdvisoryPage> createState() => _AdvisoryPageState();
}

class _AdvisoryPageState extends ConsumerState<AdvisoryPage> {
  String? _selectedFarmId;

  @override
  Widget build(BuildContext context) {
    final farmsAsync = ref.watch(myFarmsProvider);
    final showHindi = ref.watch(_showHindiProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Advisories'),
        actions: [
          TextButton(
            onPressed: () =>
                ref.read(_showHindiProvider.notifier).state = !showHindi,
            child: Text(
              showHindi ? 'EN' : 'हिं',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      body: farmsAsync.when(
        loading: () => const LoadingWidget(),
        error: (err, _) => AppErrorWidget(
          message: err.toString(),
          onRetry: () => ref.read(myFarmsProvider.notifier).refresh(),
        ),
        data: (farms) {
          if (farms.isEmpty) {
            return const EmptyStateWidget(
              icon: Icons.eco_outlined,
              message: 'No farms registered',
              subMessage: 'Register a farm to receive advisories.',
            );
          }

          _selectedFarmId ??= farms.first.id;
          final farmId = _selectedFarmId!;
          final advisoriesAsync = ref.watch(advisoriesProvider(farmId));

          return Column(
            children: [
              if (farms.length > 1)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(
                      border: Border.all(color: AppColors.border),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: DropdownButton<String>(
                      value: _selectedFarmId,
                      isExpanded: true,
                      underline: const SizedBox.shrink(),
                      items: farms
                          .map((f) => DropdownMenuItem(
                                value: f.id,
                                child: Text('${f.name} — ${f.village}'),
                              ))
                          .toList(),
                      onChanged: (v) => setState(() => _selectedFarmId = v),
                    ),
                  ),
                ),
              Expanded(
                child: advisoriesAsync.when(
                  loading: () => const LoadingWidget(),
                  error: (err, _) => AppErrorWidget(
                    message: err.toString(),
                    onRetry: () => ref.invalidate(advisoriesProvider(farmId)),
                  ),
                  data: (advisories) {
                    if (advisories.isEmpty) {
                      return const EmptyStateWidget(
                        icon: Icons.notifications_none_rounded,
                        message: 'No advisories yet',
                        subMessage:
                            'AI-generated recommendations will appear here based on your crop photos and weather data.',
                      );
                    }
                    return RefreshIndicator(
                      color: AppColors.primary,
                      onRefresh: () async =>
                          ref.invalidate(advisoriesProvider(farmId)),
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: advisories.length,
                        itemBuilder: (context, i) => _AdvisoryCard(
                          advisory: advisories[i],
                          showHindi: showHindi,
                          farmId: farmId,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _AdvisoryCard extends ConsumerWidget {
  final AdvisoryEntity advisory;
  final bool showHindi;
  final String farmId;

  const _AdvisoryCard({
    required this.advisory,
    required this.showHindi,
    required this.farmId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final color = advisoryPriorityColor(advisory.priority);
    final title = showHindi ? advisory.titleHi : advisory.titleEn;
    final body = showHindi ? advisory.bodyHi : advisory.bodyEn;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      color: advisory.isRead ? null : AppColors.primary.withValues(alpha: 0.04),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () {
          if (!advisory.isRead) {
            ref.read(advisoryRemoteDataSourceProvider).markRead(advisory.id);
            ref.invalidate(advisoriesProvider(farmId));
          }
          showDialog(
            context: context,
            builder: (_) => AlertDialog(
              shape:
                  RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              title: Text(
                title,
                style: const TextStyle(fontFamily: 'NotoSansDevanagari'),
              ),
              content: Text(
                body,
                style: const TextStyle(fontFamily: 'NotoSansDevanagari'),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Close'),
                ),
              ],
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 8,
                height: 8,
                margin: const EdgeInsets.only(top: 5),
                decoration: BoxDecoration(color: color, shape: BoxShape.circle),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontFamily: 'NotoSansDevanagari',
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      body,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                        fontFamily: 'NotoSansDevanagari',
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      advisory.createdAt.split('T').first,
                      style: const TextStyle(
                        fontSize: 10,
                        color: AppColors.textHint,
                      ),
                    ),
                  ],
                ),
              ),
              if (!advisory.isRead)
                Container(
                  width: 8,
                  height: 8,
                  margin: const EdgeInsets.only(top: 5),
                  decoration: const BoxDecoration(
                    color: AppColors.info,
                    shape: BoxShape.circle,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}