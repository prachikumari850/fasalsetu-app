import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/claims/presentation/providers/claims_provider.dart';
import 'package:fasalsetu/features/claims/domain/entities/claim_entities.dart';
import 'package:fasalsetu/features/farm/presentation/providers/farm_provider.dart';
import 'package:fasalsetu/shared/widgets/app_button.dart';
import 'package:fasalsetu/shared/widgets/app_text_field.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';

// Exact values from backend/app/models/claim.py DamageType enum.
const _damageTypes = [
  ('drought', 'Drought'),
  ('flood', 'Flood'),
  ('hail', 'Hail'),
  ('pest', 'Pest'),
  ('disease', 'Disease'),
  ('fire', 'Fire'),
  ('other', 'Other'),
];

class NewClaimPage extends ConsumerStatefulWidget {
  const NewClaimPage({super.key});

  @override
  ConsumerState<NewClaimPage> createState() => _NewClaimPageState();
}

class _NewClaimPageState extends ConsumerState<NewClaimPage> {
  String? _selectedFarmId;
  String _selectedDamageType = 'drought';
  final _descriptionController = TextEditingController();
  final _lossController = TextEditingController();
  final _acresController = TextEditingController();

  @override
  void dispose() {
    _descriptionController.dispose();
    _lossController.dispose();
    _acresController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_selectedFarmId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a farm'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final request = ClaimCreateRequest(
      farmId: _selectedFarmId!,
      damageType: _selectedDamageType,
      damageDescription: _descriptionController.text.trim().isEmpty
          ? null
          : _descriptionController.text.trim(),
      estimatedLoss: double.tryParse(_lossController.text.trim()),
      affectedAcres: double.tryParse(_acresController.text.trim()),
    );

    final created =
        await ref.read(createClaimProvider.notifier).submit(request);

    if (!mounted) return;

    if (created != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Claim submitted. Fraud analysis is running.'),
          backgroundColor: AppColors.success,
        ),
      );
      context.pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Failed to submit claim. Please try again.'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final farmsAsync = ref.watch(myFarmsProvider);
    final createState = ref.watch(createClaimProvider);
    final isSubmitting = createState.isLoading;

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
                ),
              ),
            );
          }

          _selectedFarmId ??= farms.first.id;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Farm',
                    style: TextStyle(
                        fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 8),
                Container(
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

                const SizedBox(height: 20),
                const Text('Damage Type',
                    style: TextStyle(
                        fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _damageTypes.map((dt) {
                    final selected = _selectedDamageType == dt.$1;
                    return ChoiceChip(
                      label: Text(dt.$2),
                      selected: selected,
                      selectedColor: AppColors.primary.withValues(alpha: 0.15),
                      labelStyle: TextStyle(
                        color: selected ? AppColors.primary : null,
                        fontWeight:
                            selected ? FontWeight.w600 : FontWeight.normal,
                      ),
                      onSelected: (_) =>
                          setState(() => _selectedDamageType = dt.$1),
                    );
                  }).toList(),
                ),

                const SizedBox(height: 20),
                AppTextField(
                  controller: _descriptionController,
                  label: 'Description (optional)',
                  hint: 'Describe the damage…',
                  maxLines: 3,
                ),

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

                const SizedBox(height: 28),
                AppButton(
                  label: 'Submit Claim',
                  isLoading: isSubmitting,
                  onPressed: isSubmitting ? null : _submit,
                ),
                const SizedBox(height: 24),
              ],
            ),
          );
        },
      ),
    );
  }
}