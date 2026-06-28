import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/claims/presentation/providers/claims_provider.dart';
import 'package:fasalsetu/features/claims/domain/entities/claim_entities.dart';
import 'package:fasalsetu/features/farm/presentation/providers/farm_provider.dart';
import 'package:fasalsetu/shared/widgets/app_button.dart';
import 'package:fasalsetu/shared/widgets/loading_widget.dart';
import 'package:fasalsetu/shared/widgets/error_widget.dart';

// Exact values from backend/app/models/claim.py DamageType enum.
const _damageTypes = [
  ('drought', 'Drought', Icons.water_drop_outlined),
  ('flood', 'Flood', Icons.flood_outlined),
  ('hail', 'Hail', Icons.ac_unit_rounded),
  ('pest', 'Pest', Icons.bug_report_outlined),
  ('disease', 'Disease', Icons.coronavirus_outlined),
  ('fire', 'Fire', Icons.local_fire_department_outlined),
  ('other', 'Other', Icons.help_outline_rounded),
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
  bool _submitting = false;

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

    setState(() => _submitting = true);

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
    setState(() => _submitting = false);

    if (created != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Claim submitted. Fraud analysis is running.'),
          backgroundColor: AppColors.success,
          behavior: SnackBarBehavior.floating,
        ),
      );
      context.pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Failed to submit claim. Please try again.'),
          backgroundColor: AppColors.error,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final farmsAsync = ref.watch(myFarmsProvider);

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
                const Text(
                  'Farm',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                ),
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
                              child: Text('${f.name} — ${f.village}'),
                            ))
                        .toList(),
                    onChanged: (v) => setState(() => _selectedFarmId = v),
                  ),
                ),

                const SizedBox(height: 24),
                const Text(
                  'Damage Type',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: _damageTypes.map((dt) {
                    final selected = _selectedDamageType == dt.$1;
                    return GestureDetector(
                      onTap: () =>
                          setState(() => _selectedDamageType = dt.$1),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 150),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 10),
                        decoration: BoxDecoration(
                          color: selected
                              ? AppColors.primary
                              : AppColors.surface,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: selected
                                ? AppColors.primary
                                : AppColors.border,
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              dt.$3,
                              size: 16,
                              color: selected ? Colors.white : AppColors.textSecondary,
                            ),
                            const SizedBox(width: 6),
                            Text(
                              dt.$2,
                              style: TextStyle(
                                color: selected ? Colors.white : AppColors.textPrimary,
                                fontWeight:
                                    selected ? FontWeight.w600 : FontWeight.normal,
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
                ),

                const SizedBox(height: 24),
                const Text(
                  'Description (optional)',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _descriptionController,
                  maxLines: 3,
                  decoration: InputDecoration(
                    hintText: 'Describe the damage…',
                    filled: true,
                    fillColor: AppColors.surface,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: AppColors.border),
                    ),
                  ),
                ),

                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Estimated Loss (₹)',
                            style: TextStyle(
                                fontWeight: FontWeight.w600, fontSize: 13),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _lossController,
                            keyboardType: TextInputType.number,
                            decoration: InputDecoration(
                              hintText: 'e.g. 50000',
                              filled: true,
                              fillColor: AppColors.surface,
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide(color: AppColors.border),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Affected Acres',
                            style: TextStyle(
                                fontWeight: FontWeight.w600, fontSize: 13),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _acresController,
                            keyboardType: TextInputType.number,
                            decoration: InputDecoration(
                              hintText: 'e.g. 2.5',
                              filled: true,
                              fillColor: AppColors.surface,
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide(color: AppColors.border),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 32),
                AppButton(
                  label: 'Submit Claim',
                  icon: Icons.send_rounded,
                  isLoading: _submitting,
                  onPressed: _submitting ? null : _submit,
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