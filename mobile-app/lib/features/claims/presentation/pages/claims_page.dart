// // import 'package:flutter/material.dart';

// // class ClaimsPage extends StatelessWidget {
// //   const ClaimsPage({super.key});
// //   @override
// //   Widget build(BuildContext context) => const Scaffold(
// //         body: Center(child: Text('Claims — Phase 12')),
// //       );
// // }

// import 'package:flutter/material.dart';
// import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:fasalsetu/core/constants/app_colors.dart';
// import 'package:fasalsetu/features/claims/presentation/providers/claims_provider.dart';
// import 'package:fasalsetu/shared/widgets/loading_widget.dart';
// import 'package:fasalsetu/shared/widgets/error_widget.dart';

// class ClaimsPage extends ConsumerWidget {
//   const ClaimsPage({super.key});

//   Color _statusColor(String status) {
//     switch (status) {
//       case 'approved': return Colors.green;
//       case 'rejected': return Colors.red;
//       case 'needs_inspection': return Colors.purple;
//       case 'under_review': return Colors.amber;
//       default: return Colors.blue;
//     }
//   }

//   @override
//   Widget build(BuildContext context, WidgetRef ref) {
//     final claimsAsync = ref.watch(claimsListProvider);

//     return Scaffold(
//       backgroundColor: AppColors.background,
//       appBar: AppBar(title: const Text('Claims')),
//       body: claimsAsync.when(
//         loading: () => const LoadingWidget(),
//         error: (err, _) => AppErrorWidget(
//           message: err.toString(),
//           onRetry: () => ref.invalidate(claimsListProvider),
//         ),
//         data: (claims) {
//           if (claims.isEmpty) {
//             return const Center(child: Text('No claims submitted yet.'));
//           }
//           return RefreshIndicator(
//             onRefresh: () async => ref.invalidate(claimsListProvider),
//             child: ListView.builder(
//               padding: const EdgeInsets.all(12),
//               itemCount: claims.length,
//               itemBuilder: (context, i) {
//                 final c = claims[i];
//                 return Card(
//                   margin: const EdgeInsets.only(bottom: 10),
//                   child: ListTile(
//                     title: Text(c.damageType.toUpperCase()),
//                     subtitle: Text('Submitted: ${c.submittedAt ?? "—"}'),
//                     trailing: Chip(
//                       label: Text(c.status.replaceAll('_', ' ')),
//                       backgroundColor: _statusColor(c.status).withOpacity(0.15),
//                       labelStyle: TextStyle(color: _statusColor(c.status)),
//                     ),
//                   ),
//                 );
//               },
//             ),
//           );
//         },
//       ),
//     );
//   }
// }

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

Color claimStatusColor(String status) {
  switch (status) {
    case 'approved':
      return AppColors.statusApproved;
    case 'rejected':
      return AppColors.statusRejected;
    case 'needs_inspection':
      return AppColors.statusInspection;
    case 'under_review':
      return AppColors.statusUnderReview;
    case 'submitted':
      return AppColors.statusSubmitted;
    default:
      return AppColors.statusDraft;
  }
}

String claimStatusLabel(String status) {
  switch (status) {
    case 'needs_inspection':
      return 'Needs Inspection';
    case 'under_review':
      return 'Under Review';
    default:
      return status.isEmpty
          ? status
          : status[0].toUpperCase() + status.substring(1);
  }
}

/// Claims endpoint only returns a bare trust_score number, not a letter
/// grade, so we derive the grade locally using the same thresholds the
/// backend uses in fraud.py's _compute_trust_grade().
TrustScoreEntity claimSummaryToTrust(ClaimSummary claim) {
  final score = claim.trustScore;
  String? grade;
  if (score != null) {
    if (score >= 80) {
      grade = 'A';
    } else if (score >= 60) {
      grade = 'B';
    } else if (score >= 40) {
      grade = 'C';
    } else if (score >= 20) {
      grade = 'D';
    } else {
      grade = 'F';
    }
  }
  return TrustScoreEntity(farmId: claim.farmId, score: score, grade: grade);
}

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
                          'Submit an insurance claim from your farm if you have suffered crop damage.',
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
              padding: const EdgeInsets.all(16),
              itemCount: claims.length,
              itemBuilder: (context, i) {
                final c = claims[i];
                final color = claimStatusColor(c.status);
                return Card(
                  margin: const EdgeInsets.only(bottom: 10),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () => context.push('/claims/${c.id}'),
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: color.withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Icon(Icons.description_rounded,
                                color: color, size: 20),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  c.damageType
                                      .replaceAll('_', ' ')
                                      .toUpperCase(),
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w600,
                                    fontSize: 13,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  c.submittedAt != null
                                      ? c.submittedAt!.split('T').first
                                      : '—',
                                  style: const TextStyle(
                                    fontSize: 11,
                                    color: AppColors.textSecondary,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          if (c.trustScore != null) ...[
                            TrustScoreBadge(trust: claimSummaryToTrust(c)),
                            const SizedBox(width: 8),
                          ],
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: color.withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              claimStatusLabel(c.status),
                              style: TextStyle(
                                color: color,
                                fontSize: 10,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/claims/new'),
        backgroundColor: AppColors.primary,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }
}