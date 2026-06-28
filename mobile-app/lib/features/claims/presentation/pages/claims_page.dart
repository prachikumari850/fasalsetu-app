// lib/features/claims/presentation/pages/claims_page.dart
// Confirmed working against:
//   - ClaimsRemoteDataSource.listClaims() → GET /claims
//   - ClaimsListNotifier (AsyncNotifier with .refresh())
//   - ClaimSummary entity (id, farmId, status, damageType, trustScore, submittedAt)
//   - TrustScoreEntity + TrustScoreBadge (from trust/domain + trust/presentation)
//   - AppColors.status* and AppColors.priority* constants
//   - AppErrorWidget, LoadingWidget, EmptyStateWidget from shared/widgets

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/claims/presentation/providers/claims_provider.dart';
import 'package:fasalsetu/features/claims/domain/entities/claim_entities.dart';
import 'package:fasalsetu/features/trust/presentation/widgets/trust_score_widget.dart';
import 'package:fasalsetu/features/trust/domain/entities/trust_entities.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';
import 'package:fasalsetu/shared/widgets/empty_state_widget.dart';

// ── Helpers ───────────────────────────────────────────────────────────────────

Color claimStatusColor(String status) {
  switch (status) {
    case 'approved':         return AppColors.statusApproved;
    case 'rejected':         return AppColors.statusRejected;
    case 'needs_inspection': return AppColors.statusInspection;
    case 'under_review':     return AppColors.statusUnderReview;
    case 'submitted':        return AppColors.statusSubmitted;
    default:                 return AppColors.statusDraft;
  }
}

String claimStatusLabel(String status) {
  switch (status) {
    case 'needs_inspection': return 'Needs Inspection';
    case 'under_review':     return 'Under Review';
    case '':                 return 'Draft';
    default:
      return status[0].toUpperCase() + status.substring(1);
  }
}

String damageTypeLabel(String type) {
  switch (type) {
    case 'drought': return 'Drought';
    case 'flood':   return 'Flood';
    case 'hail':    return 'Hail';
    case 'pest':    return 'Pest';
    case 'disease': return 'Disease';
    case 'fire':    return 'Fire';
    default:        return 'Other';
  }
}

IconData damageTypeIcon(String type) {
  switch (type) {
    case 'drought': return Icons.wb_sunny_outlined;
    case 'flood':   return Icons.water_outlined;
    case 'hail':    return Icons.ac_unit_outlined;
    case 'pest':    return Icons.pest_control_outlined;
    case 'disease': return Icons.coronavirus_outlined;
    case 'fire':    return Icons.local_fire_department_outlined;
    default:        return Icons.help_outline_rounded;
  }
}

// Derive grade from score using same thresholds as backend fraud.py
TrustScoreEntity _toTrust(ClaimSummary claim) {
  final score = claim.trustScore;
  String? grade;
  if (score != null) {
    if (score >= 80)      grade = 'A';
    else if (score >= 60) grade = 'B';
    else if (score >= 40) grade = 'C';
    else if (score >= 20) grade = 'D';
    else                  grade = 'F';
  }
  return TrustScoreEntity(farmId: claim.farmId, score: score, grade: grade);
}

// ── Page ─────────────────────────────────────────────────────────────────────

class ClaimsPage extends ConsumerWidget {
  const ClaimsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final claimsAsync = ref.watch(claimsListProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Claims'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.read(claimsListProvider.notifier).refresh(),
          ),
        ],
      ),
      body: claimsAsync.when(
        loading: () => const LoadingWidget(),
        error: (err, _) => AppErrorWidget(
          message: err.toString(),
          onRetry: () => ref.read(claimsListProvider.notifier).refresh(),
        ),
        data: (claims) {
          if (claims.isEmpty) {
            return RefreshIndicator(
              color: AppColors.primary,
              onRefresh: () => ref.read(claimsListProvider.notifier).refresh(),
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  SizedBox(
                    height: MediaQuery.of(context).size.height * 0.7,
                    child: const EmptyStateWidget(
                      icon: Icons.description_outlined,
                      message: 'No claims submitted yet',
                      subMessage:
                          'Tap + to submit a crop damage insurance claim.',
                    ),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            color: AppColors.primary,
            onRefresh: () => ref.read(claimsListProvider.notifier).refresh(),
            child: ListView.builder(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 96),
              itemCount: claims.length,
              itemBuilder: (context, i) => _ClaimCard(claim: claims[i]),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/claims/new'),
        backgroundColor: AppColors.primary,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text(
          'New Claim',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
        ),
      ),
    );
  }
}

class _ClaimCard extends StatelessWidget {
  final ClaimSummary claim;
  const _ClaimCard({required this.claim});

  @override
  Widget build(BuildContext context) {
    final color  = claimStatusColor(claim.status);
    final trust  = _toTrust(claim);
    final date   = claim.submittedAt?.split('T').first ?? '—';

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () => context.push('/claims/${claim.id}'),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              // Icon
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  damageTypeIcon(claim.damageType),
                  color: color,
                  size: 22,
                ),
              ),
              const SizedBox(width: 12),

              // Text
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      damageTypeLabel(claim.damageType),
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      'Submitted: $date',
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),

              // Trust badge + status chip
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      claimStatusLabel(claim.status),
                      style: TextStyle(
                        color: color,
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  if (trust.hasScore) ...[
                    const SizedBox(height: 6),
                    TrustScoreBadge(trust: trust),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}