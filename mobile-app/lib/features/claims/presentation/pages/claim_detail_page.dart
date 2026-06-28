// lib/features/claims/presentation/pages/claim_detail_page.dart
// Contains TWO classes:
//   1. NewClaimPage  → route /claims/new
//   2. ClaimDetailPage → route /claims/:claimId
// Wired to:
//   - createClaimProvider (CreateClaimNotifier) → POST /claims
//   - claimDetailProvider(claimId) → GET /claims/:id
//   - myFarmsProvider (farm picker)
//   - ClaimCreateRequest, ClaimDetail entities
//   - AppButton, AppTextField, AppErrorWidget, LoadingWidget from confirmed paths

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/claims/presentation/providers/claims_provider.dart';
import 'package:fasalsetu/features/claims/domain/entities/claim_entities.dart';
import 'package:fasalsetu/features/farm/presentation/providers/farm_provider.dart';
import 'package:fasalsetu/features/trust/presentation/widgets/trust_score_widget.dart';
import 'package:fasalsetu/features/trust/domain/entities/trust_entities.dart';
import 'package:fasalsetu/shared/widgets/app_button.dart';
import 'package:fasalsetu/shared/widgets/app_text_field.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';

// Exact values from backend/app/models/claim.py DamageType enum
const _damageTypes = [
  ('drought', 'Drought',  Icons.wb_sunny_outlined),
  ('flood',   'Flood',    Icons.water_outlined),
  ('hail',    'Hail',     Icons.ac_unit_outlined),
  ('pest',    'Pest',     Icons.pest_control_outlined),
  ('disease', 'Disease',  Icons.coronavirus_outlined),
  ('fire',    'Fire',     Icons.local_fire_department_outlined),
  ('other',   'Other',    Icons.help_outline_rounded),
];

TrustScoreEntity _toTrust(ClaimDetail claim) {
  final score = claim.trustScore;
  String? grade;
  if (score != null) {
    if (score >= 80)      grade = 'A';
    else if (score >= 60) grade = 'B';
    else if (score >= 40) grade = 'C';
    else if (score >= 20) grade = 'D';
    else                  grade = 'F';
  }
  return TrustScoreEntity(
      farmId: claim.farmId, score: score, grade: grade);
}

// ═══════════════════════════════════════════════════════════════════════════
// 1. NEW CLAIM PAGE  (/claims/new)
// ═══════════════════════════════════════════════════════════════════════════

class NewClaimPage extends ConsumerStatefulWidget {
  const NewClaimPage({super.key});

  @override
  ConsumerState<NewClaimPage> createState() => _NewClaimPageState();
}

class _NewClaimPageState extends ConsumerState<NewClaimPage> {
  String? _selectedFarmId;
  String  _selectedDamageType = 'drought';
  final   _descController     = TextEditingController();
  final   _lossController     = TextEditingController();
  final   _acresController    = TextEditingController();
  final   _formKey            = GlobalKey<FormState>();

  @override
  void dispose() {
    _descController.dispose();
    _lossController.dispose();
    _acresController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    if (_selectedFarmId == null) {
      _snack('Please select a farm', isError: true);
      return;
    }

    final request = ClaimCreateRequest(
      farmId:           _selectedFarmId!,
      damageType:       _selectedDamageType,
      damageDescription: _descController.text.trim().isEmpty
          ? null
          : _descController.text.trim(),
      estimatedLoss:  double.tryParse(_lossController.text.trim()),
      affectedAcres:  double.tryParse(_acresController.text.trim()),
    );

    final created =
        await ref.read(createClaimProvider.notifier).submit(request);

    if (!mounted) return;

    if (created != null) {
      _snack('Claim submitted. Fraud analysis is running.');
      context.pop();
    } else {
      _snack('Failed to submit claim. Please try again.', isError: true);
    }
  }

  void _snack(String msg, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg),
      backgroundColor: isError ? AppColors.error : AppColors.success,
    ));
  }

  @override
  Widget build(BuildContext context) {
    final farmsAsync  = ref.watch(myFarmsProvider);
    final isSubmitting = ref.watch(createClaimProvider).isLoading;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Submit Claim'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => context.pop(),
        ),
      ),
      body: farmsAsync.when(
        loading: () => const LoadingWidget(),
        error: (e, _) => AppErrorWidget(
          message: e.toString(),
          onRetry: () => ref.read(myFarmsProvider.notifier).refresh(),
        ),
        data: (farms) {
          if (farms.isEmpty) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: Text(
                  'Register a farm before submitting a claim.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: AppColors.textSecondary),
                ),
              ),
            );
          }

          _selectedFarmId ??= farms.first.id;

          return Form(
            key: _formKey,
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 40),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Farm picker ────────────────────────────────────────
                  _SectionLabel('Select Farm'),
                  const SizedBox(height: 8),
                  Container(
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

                  // ── Damage type ────────────────────────────────────────
                  const SizedBox(height: 20),
                  _SectionLabel('Damage Type'),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _damageTypes.map((dt) {
                      final selected = _selectedDamageType == dt.$1;
                      return FilterChip(
                        avatar: Icon(
                          dt.$3,
                          size: 16,
                          color: selected
                              ? AppColors.primary
                              : AppColors.textSecondary,
                        ),
                        label: Text(dt.$2),
                        selected: selected,
                        selectedColor:
                            AppColors.primary.withValues(alpha: 0.15),
                        checkmarkColor: AppColors.primary,
                        labelStyle: TextStyle(
                          color: selected
                              ? AppColors.primary
                              : AppColors.textSecondary,
                          fontWeight: selected
                              ? FontWeight.w600
                              : FontWeight.normal,
                        ),
                        onSelected: (_) =>
                            setState(() => _selectedDamageType = dt.$1),
                      );
                    }).toList(),
                  ),

                  // ── Description ────────────────────────────────────────
                  const SizedBox(height: 20),
                  AppTextField(
                    controller: _descController,
                    label: 'Description (optional)',
                    hint: 'Describe the damage in detail…',
                    maxLines: 3,
                  ),

                  // ── Loss + acres ───────────────────────────────────────
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: AppTextField(
                          controller: _lossController,
                          label: 'Estimated Loss (₹)',
                          hint: 'e.g. 50000',
                          keyboardType: TextInputType.number,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: AppTextField(
                          controller: _acresController,
                          label: 'Affected Acres',
                          hint: 'e.g. 2.5',
                          keyboardType: TextInputType.number,
                        ),
                      ),
                    ],
                  ),

                  // ── Info banner ────────────────────────────────────────
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.info.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                          color: AppColors.info.withValues(alpha: 0.2)),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.info_outline_rounded,
                            size: 16, color: AppColors.info),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'After submission, a fraud analysis will run automatically and a trust score will be assigned.',
                            style: TextStyle(
                                fontSize: 12, color: AppColors.info),
                          ),
                        ),
                      ],
                    ),
                  ),

                  // ── Submit button ──────────────────────────────────────
                  const SizedBox(height: 28),
                  AppButton(
                    label: 'Submit Claim',
                    isLoading: isSubmitting,
                    icon: Icons.send_rounded,
                    onPressed: isSubmitting ? null : _submit,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 2. CLAIM DETAIL PAGE  (/claims/:claimId)
// ═══════════════════════════════════════════════════════════════════════════

class ClaimDetailPage extends ConsumerWidget {
  final String claimId;
  const ClaimDetailPage({super.key, required this.claimId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final claimAsync = ref.watch(claimDetailProvider(claimId));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Claim Details'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.invalidate(claimDetailProvider(claimId)),
          ),
        ],
      ),
      body: claimAsync.when(
        loading: () => const LoadingWidget(),
        error: (e, _) => AppErrorWidget(
          message: e.toString(),
          onRetry: () => ref.invalidate(claimDetailProvider(claimId)),
        ),
        data: (claim) => _ClaimDetailBody(claim: claim),
      ),
    );
  }
}

class _ClaimDetailBody extends StatelessWidget {
  final ClaimDetail claim;
  const _ClaimDetailBody({required this.claim});

  String get _statusLabel {
    switch (claim.status) {
      case 'needs_inspection': return 'Needs Inspection';
      case 'under_review':     return 'Under Review';
      case '':                 return 'Draft';
      default:
        return claim.status[0].toUpperCase() + claim.status.substring(1);
    }
  }

  Color get _statusColor {
    switch (claim.status) {
      case 'approved':         return AppColors.statusApproved;
      case 'rejected':         return AppColors.statusRejected;
      case 'needs_inspection': return AppColors.statusInspection;
      case 'under_review':     return AppColors.statusUnderReview;
      case 'submitted':        return AppColors.statusSubmitted;
      default:                 return AppColors.statusDraft;
    }
  }

  @override
  Widget build(BuildContext context) {
    final trust = _toTrust(claim);

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Status card ────────────────────────────────────────────────
          Card(
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _statusColor.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(Icons.description_rounded,
                        color: _statusColor, size: 28),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          claim.damageType
                              .replaceAll('_', ' ')
                              .toUpperCase(),
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 3),
                          decoration: BoxDecoration(
                            color: _statusColor.withValues(alpha: 0.12),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            _statusLabel,
                            style: TextStyle(
                              color: _statusColor,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // ── Trust score card ───────────────────────────────────────────
          const SizedBox(height: 12),
          TrustScoreCard(trust: trust),

          // ── Details ────────────────────────────────────────────────────
          const SizedBox(height: 12),
          Card(
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Claim Details',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (claim.damageDescription != null) ...[
                    _DetailRow(
                        label: 'Description',
                        value: claim.damageDescription!),
                    const Divider(height: 20),
                  ],
                  if (claim.estimatedLoss != null)
                    _DetailRow(
                      label: 'Estimated Loss',
                      value:
                          '₹${claim.estimatedLoss!.toStringAsFixed(0)}',
                    ),
                  if (claim.affectedAcres != null) ...[
                    const SizedBox(height: 8),
                    _DetailRow(
                      label: 'Affected Acres',
                      value:
                          '${claim.affectedAcres!.toStringAsFixed(2)} acres',
                    ),
                  ],
                  if (claim.submittedAt != null) ...[
                    const SizedBox(height: 8),
                    _DetailRow(
                      label: 'Submitted',
                      value: claim.submittedAt!.split('T').first,
                    ),
                  ],
                  if (claim.reviewedAt != null) ...[
                    const SizedBox(height: 8),
                    _DetailRow(
                      label: 'Reviewed',
                      value: claim.reviewedAt!.split('T').first,
                    ),
                  ],
                ],
              ),
            ),
          ),

          // ── Fraud flags ────────────────────────────────────────────────
          if (claim.fraudAnalyzed && claim.fraudFlags.isNotEmpty) ...[
            const SizedBox(height: 12),
            Card(
              color: AppColors.error.withValues(alpha: 0.05),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
                side: BorderSide(
                    color: AppColors.error.withValues(alpha: 0.2)),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.flag_rounded,
                            color: AppColors.error, size: 18),
                        SizedBox(width: 8),
                        Text(
                          'Fraud Flags',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                            color: AppColors.error,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    ...claim.fraudFlags.map((flag) => Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(Icons.circle,
                                  size: 6,
                                  color: AppColors.error),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  flag.replaceAll('_', ' '),
                                  style: const TextStyle(
                                    fontSize: 13,
                                    color: AppColors.textSecondary,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        )),
                  ],
                ),
              ),
            ),
          ],

          // ── Officer notes ──────────────────────────────────────────────
          if (claim.officerNotes != null &&
              claim.officerNotes!.isNotEmpty) ...[
            const SizedBox(height: 12),
            Card(
              color: AppColors.info.withValues(alpha: 0.05),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
                side: BorderSide(
                    color: AppColors.info.withValues(alpha: 0.2)),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.notes_rounded,
                            color: AppColors.info, size: 18),
                        SizedBox(width: 8),
                        Text(
                          'Officer Notes',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                            color: AppColors.info,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      claim.officerNotes!,
                      style: const TextStyle(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;
  const _DetailRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 120,
          child: Text(
            label,
            style: const TextStyle(
                fontSize: 13, color: AppColors.textSecondary),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: AppColors.textPrimary),
          ),
        ),
      ],
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String text;
  const _SectionLabel(this.text);

  @override
  Widget build(BuildContext context) => Text(
        text,
        style: const TextStyle(
          fontWeight: FontWeight.w600,
          fontSize: 13,
          color: AppColors.textSecondary,
        ),
      );
}