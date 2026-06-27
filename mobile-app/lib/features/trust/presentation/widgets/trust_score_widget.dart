import 'package:flutter/material.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/trust/domain/entities/trust_entities.dart';

Color gradeColor(String? grade) {
  switch (grade) {
    case 'A':
      return AppColors.gradeA;
    case 'B':
      return AppColors.gradeB;
    case 'C':
      return AppColors.gradeC;
    case 'D':
      return AppColors.gradeD;
    case 'F':
      return AppColors.gradeF;
    default:
      return AppColors.textHint;
  }
}

String gradeDescription(String? grade) {
  switch (grade) {
    case 'A':
      return 'Highly trusted farm record';
    case 'B':
      return 'Trusted — standard processing';
    case 'C':
      return 'Moderate trust — may need review';
    case 'D':
      return 'Low trust — inspection likely';
    case 'F':
      return 'Very low trust';
    default:
      return 'No score yet';
  }
}

/// Compact badge — used inline on cards/lists.
class TrustScoreBadge extends StatelessWidget {
  final TrustScoreEntity trust;
  const TrustScoreBadge({super.key, required this.trust});

  @override
  Widget build(BuildContext context) {
    if (!trust.hasScore) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(8),
        ),
        child: const Text(
          'Not scored',
          style: TextStyle(fontSize: 11, color: AppColors.textHint),
        ),
      );
    }
    final color = gradeColor(trust.grade);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            trust.grade ?? '?',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
              fontSize: 13,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            trust.score!.toStringAsFixed(0),
            style: TextStyle(color: color, fontSize: 12),
          ),
        ],
      ),
    );
  }
}

/// Large circular card — used as a banner/section header.
class TrustScoreCard extends StatelessWidget {
  final TrustScoreEntity trust;
  const TrustScoreCard({super.key, required this.trust});

  @override
  Widget build(BuildContext context) {
    final color = gradeColor(trust.grade);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: color.withValues(alpha: 0.12),
                border: Border.all(color: color, width: 2),
              ),
              child: Center(
                child: trust.hasScore
                    ? Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            trust.grade ?? '?',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: color,
                            ),
                          ),
                          Text(
                            trust.score!.toStringAsFixed(0),
                            style: TextStyle(fontSize: 11, color: color),
                          ),
                        ],
                      )
                    : Icon(Icons.help_outline_rounded, color: color),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Trust Score',
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    trust.hasScore
                        ? gradeDescription(trust.grade)
                        : (trust.message ??
                            'Submit a claim to generate a trust score.'),
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}