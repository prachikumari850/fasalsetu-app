import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/analysis/presentation/providers/analysis_provider.dart';
import 'package:fasalsetu/features/analysis/domain/entities/analysis_entities.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';
import 'package:fasalsetu/shared/widgets/empty_state_widget.dart';

class ImageAnalysisPage extends ConsumerWidget {
  final String farmId;
  final String imageId;
  final String imageUrl;

  const ImageAnalysisPage({
    super.key,
    required this.farmId,
    required this.imageId,
    required this.imageUrl,
  });

  Color _severityColor(String severity) {
    switch (severity) {
      case 'critical':
        return AppColors.statusRejected;
      case 'high':
        return AppColors.error;
      case 'medium':
        return AppColors.warning;
      case 'low':
        return AppColors.success;
      default:
        return AppColors.textHint;
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final params = AnalysisParams(farmId: farmId, imageId: imageId);
    final analysisAsync = ref.watch(imageAnalysisProvider(params));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Disease Detection'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.invalidate(imageAnalysisProvider(params)),
          ),
        ],
      ),
      body: analysisAsync.when(
        loading: () => const LoadingWidget(),
        error: (e, _) => AppErrorWidget(
          message: e.toString(),
          onRetry: () => ref.invalidate(imageAnalysisProvider(params)),
        ),
        data: (analysis) => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: AspectRatio(
                  aspectRatio: 1,
                  child: CachedNetworkImage(
                    imageUrl: imageUrl,
                    fit: BoxFit.cover,
                    placeholder: (_, __) => Container(
                      color: AppColors.surfaceVariant,
                      child: const Center(
                        child: CircularProgressIndicator(
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                    errorWidget: (_, __, ___) => Container(
                      color: AppColors.surfaceVariant,
                      child: const Icon(
                        Icons.broken_image_outlined,
                        size: 48,
                        color: AppColors.textHint,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    analysis.isInsideFence
                        ? Icons.check_circle_rounded
                        : Icons.warning_amber_rounded,
                    size: 16,
                    color: analysis.isInsideFence
                        ? AppColors.success
                        : AppColors.warning,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    analysis.isInsideFence
                        ? 'Photo taken inside farm boundary'
                        : 'Photo taken outside farm boundary',
                    style: TextStyle(
                      fontSize: 12,
                      color: analysis.isInsideFence
                          ? AppColors.success
                          : AppColors.warning,
                    ),
                  ),
                  const Spacer(),
                  if (!analysis.aiProcessed)
                    const Text(
                      'Analysis pending…',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textHint,
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 20),
              const Text(
                'AI Detection Results',
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
              ),
              const SizedBox(height: 12),
              if (analysis.reports.isEmpty)
                EmptyStateWidget(
                  icon: Icons.bug_report_outlined,
                  message: analysis.aiProcessed
                      ? 'No disease detected'
                      : 'Analysis not completed yet',
                  subMessage: analysis.aiProcessed
                      ? 'This photo looks healthy.'
                      : 'Check back shortly — the AI model is still processing.',
                )
              else
                ...analysis.reports.map((r) => _DiseaseReportCard(
                      report: r,
                      color: _severityColor(r.severity),
                    )),
            ],
          ),
        ),
      ),
    );
  }
}

class _DiseaseReportCard extends StatelessWidget {
  final DiseaseReportEntity report;
  final Color color;

  const _DiseaseReportCard({required this.report, required this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(Icons.bug_report_rounded, color: color, size: 18),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    report.diseaseName.replaceAll('_', ' ').toUpperCase(),
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 3,
                  ),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    report.severity.toUpperCase(),
                    style: TextStyle(
                      color: color,
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Text(
                  'Confidence: ',
                  style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                ),
                Text(
                  '${(report.confidence * 100).toStringAsFixed(1)}%',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: report.confidence,
                backgroundColor: AppColors.surfaceVariant,
                color: color,
                minHeight: 5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}