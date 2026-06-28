// lib/features/advisory/presentation/pages/advisory_page.dart
// Wired to:
//   - advisoriesProvider(farmId) → AdvisoryRemoteDataSource.getAdvisories(farmId)
//     → GET /api/v1/advisories/{farm_id}  ✓ matches backend route "/{farm_id}"
//   - advisoryRemoteDataSourceProvider.markRead(id) → PUT /advisories/{id}/read
//   - myFarmsProvider (MyFarmsNotifier) for farm picker
//   - AdvisoryEntity (id,farmId,titleEn,titleHi,bodyEn,bodyHi,priority,isRead,createdAt)
//   - AppColors.priority* constants confirmed in app_colors.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/advisory/presentation/providers/advisory_provider.dart';
import 'package:fasalsetu/features/advisory/domain/entities/advisory_entities.dart';
import 'package:fasalsetu/features/farm/presentation/providers/farm_provider.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';
import 'package:fasalsetu/shared/widgets/empty_state_widget.dart';

// ── Helpers ───────────────────────────────────────────────────────────────────

Color _priorityColor(String priority) {
  switch (priority) {
    case 'urgent': return AppColors.priorityUrgent;
    case 'high':   return AppColors.priorityHigh;
    case 'medium': return AppColors.priorityMedium;
    default:       return AppColors.priorityLow;
  }
}

String _priorityLabel(String priority) {
  switch (priority) {
    case 'urgent': return 'Urgent';
    case 'high':   return 'High';
    case 'medium': return 'Medium';
    default:       return 'Low';
  }
}

// Language toggle: true = Hindi, false = English
final _showHindiProvider = StateProvider<bool>((ref) => true);

// ── Page ─────────────────────────────────────────────────────────────────────

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
    final showHindi  = ref.watch(_showHindiProvider);

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
                fontSize: 15,
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () {
              if (_selectedFarmId != null) {
                ref.invalidate(advisoriesProvider(_selectedFarmId!));
              }
            },
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
              subMessage: 'Register a farm to receive AI advisories.',
            );
          }

          // initialise on first build
          _selectedFarmId ??= farms.first.id;
          final farmId        = _selectedFarmId!;
          final advisoriesAsync = ref.watch(advisoriesProvider(farmId));

          return Column(
            children: [
              // Farm picker — only show when more than one farm
              if (farms.length > 1)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
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
                                child: Text(
                                  '${f.name} — ${f.village}',
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ))
                          .toList(),
                      onChanged: (v) => setState(() => _selectedFarmId = v),
                    ),
                  ),
                ),

              // Advisory list
              Expanded(
                child: advisoriesAsync.when(
                  loading: () => const LoadingWidget(),
                  error: (err, _) => AppErrorWidget(
                    message: err.toString(),
                    onRetry: () =>
                        ref.invalidate(advisoriesProvider(farmId)),
                  ),
                  data: (advisories) {
                    if (advisories.isEmpty) {
                      return const EmptyStateWidget(
                        icon: Icons.notifications_none_rounded,
                        message: 'No advisories yet',
                        subMessage:
                            'AI recommendations will appear here after you upload crop photos.',
                      );
                    }

                    return RefreshIndicator(
                      color: AppColors.primary,
                      onRefresh: () async =>
                          ref.invalidate(advisoriesProvider(farmId)),
                      child: ListView.builder(
                        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
                        itemCount: advisories.length,
                        itemBuilder: (context, i) => _AdvisoryCard(
                          advisory:  advisories[i],
                          showHindi: showHindi,
                          farmId:    farmId,
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

// ── Advisory Card ─────────────────────────────────────────────────────────────

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
    final color = _priorityColor(advisory.priority);
    final title = showHindi ? advisory.titleHi : advisory.titleEn;
    final body  = showHindi ? advisory.bodyHi  : advisory.bodyEn;
    final date  = advisory.createdAt.split('T').first;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      color: advisory.isRead
          ? AppColors.surface
          : AppColors.primary.withValues(alpha: 0.04),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () {
          // Mark as read then refresh
          if (!advisory.isRead) {
            ref
                .read(advisoryRemoteDataSourceProvider)
                .markRead(advisory.id)
                .then((_) => ref.invalidate(advisoriesProvider(farmId)))
                .catchError((_) {});
          }
          _showDetail(context, title, body);
        },
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Priority dot
              Padding(
                padding: const EdgeInsets.only(top: 5),
                child: Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
              const SizedBox(width: 12),

              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            title,
                            style: TextStyle(
                              fontWeight: advisory.isRead
                                  ? FontWeight.w500
                                  : FontWeight.bold,
                              fontSize: 14,
                              color: AppColors.textPrimary,
                              fontFamily: showHindi
                                  ? 'NotoSansDevanagari'
                                  : null,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        // Priority chip
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 7, vertical: 2),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.12),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            _priorityLabel(advisory.priority),
                            style: TextStyle(
                              fontSize: 10,
                              color: color,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 5),
                    Text(
                      body,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                        fontFamily: showHindi ? 'NotoSansDevanagari' : null,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        const Icon(Icons.calendar_today_outlined,
                            size: 11, color: AppColors.textHint),
                        const SizedBox(width: 4),
                        Text(
                          date,
                          style: const TextStyle(
                            fontSize: 11,
                            color: AppColors.textHint,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Unread dot
              if (!advisory.isRead)
                Padding(
                  padding: const EdgeInsets.only(left: 8, top: 4),
                  child: Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: AppColors.info,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _showDetail(BuildContext context, String title, String body) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16)),
        title: Text(
          title,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
            fontFamily: showHindi ? 'NotoSansDevanagari' : null,
          ),
        ),
        content: SingleChildScrollView(
          child: Text(
            body,
            style: TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
              fontFamily: showHindi ? 'NotoSansDevanagari' : null,
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              'Close',
              style: TextStyle(color: AppColors.primary),
            ),
          ),
        ],
      ),
    );
  }
}