import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fasalsetu/l10n/app_localizations.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/crop/domain/entities/crop_entities.dart';
import 'package:fasalsetu/features/crop/presentation/providers/crop_provider.dart';
import 'package:fasalsetu/features/crop/presentation/widgets/stage_card_widget.dart';
import 'package:fasalsetu/features/trust/presentation/providers/trust_provider.dart';
import 'package:fasalsetu/features/trust/presentation/widgets/trust_score_widget.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';

class CropLifecyclePage extends ConsumerWidget {
  final String farmId;
  final String farmName;

  const CropLifecyclePage({
    super.key,
    required this.farmId,
    required this.farmName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final timelineAsync = ref.watch(cropTimelineProvider(farmId));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.cropLifecycle),
            Text(
              farmName,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.white70,
              ),
            ),
          ],
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.health_and_safety_outlined),
            tooltip: 'Crop Health',
            onPressed: () => context.push(
              '/farms/$farmId/health?name=${Uri.encodeComponent(farmName)}',
            ),
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () =>
                ref.read(cropTimelineProvider(farmId).notifier).refresh(farmId),
          ),
        ],
      ),
      body: RefreshIndicator(
        color: AppColors.primary,
        onRefresh: () =>
            ref.read(cropTimelineProvider(farmId).notifier).refresh(farmId),
        child: timelineAsync.when(
          loading: () => const LoadingWidget(),
          error: (e, _) => AppErrorWidget(
            message: e.toString(),
            onRetry: () =>
                ref.read(cropTimelineProvider(farmId).notifier).refresh(farmId),
          ),
          data: (timeline) => _TimelineBody(
            timeline: timeline,
            farmId: farmId,
          ),
        ),
      ),
    );
  }
}

class _TimelineBody extends ConsumerWidget {
  final CropTimelineEntity timeline;
  final String farmId;

  const _TimelineBody({
    required this.timeline,
    required this.farmId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final trustAsync = ref.watch(trustScoreProvider(farmId));

    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: Column(
        children: [
          // Progress summary banner
          Container(
            width: double.infinity,
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.primary,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.cropLifecycle,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                          fontFamily: 'NotoSansDevanagari',
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${timeline.completedStages}/5 stages completed',
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                          fontFamily: 'NotoSansDevanagari',
                        ),
                      ),
                      const SizedBox(height: 8),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: timeline.completedStages / 5,
                          backgroundColor: Colors.white24,
                          valueColor: const AlwaysStoppedAnimation(
                            Colors.white,
                          ),
                          minHeight: 6,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Column(
                  children: [
                    Text(
                      '${timeline.totalImages}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Text(
                      'Photos',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 11,
                        fontFamily: 'NotoSansDevanagari',
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Trust score card
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
            child: trustAsync.when(
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
              data: (trust) => TrustScoreCard(trust: trust),
            ),
          ),

          // Stage cards
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
            itemCount: timeline.stages.length,
            separatorBuilder: (_, __) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final timelineStage = timeline.stages[index];
              final isLast = index == timeline.stages.length - 1;
              return StageCardWidget(
                timelineStage: timelineStage,
                farmId: farmId,
                stageIndex: index,
                showConnector: !isLast,
              );
            },
          ),
        ],
      ),
    );
  }
}