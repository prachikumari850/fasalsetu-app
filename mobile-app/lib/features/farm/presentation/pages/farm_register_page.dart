import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fasalsetu/l10n/app_localizations.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/farm/presentation/providers/farm_provider.dart';
import 'package:fasalsetu/features/farm/presentation/widgets/boundary_map_widget.dart';
import 'package:fasalsetu/shared/widgets/app_button.dart';
import 'package:fasalsetu/shared/widgets/app_text_field.dart';
import 'package:latlong2/latlong.dart';

class FarmRegisterPage extends ConsumerStatefulWidget {
  const FarmRegisterPage({super.key});

  @override
  ConsumerState<FarmRegisterPage> createState() => _FarmRegisterPageState();
}

class _FarmRegisterPageState extends ConsumerState<FarmRegisterPage> {
  final _formKey = GlobalKey<FormState>();
  int _currentStep = 0;

  // Form controllers
  final _nameCtrl = TextEditingController();
  final _villageCtrl = TextEditingController();
  final _talukaCtrl = TextEditingController();
  final _districtCtrl = TextEditingController();
  final _stateCtrl = TextEditingController(text: 'Uttar Pradesh');
  final _areaCtrl = TextEditingController();
  final _cropCtrl = TextEditingController();
  final _seasonCtrl = TextEditingController();
  final _khasraCtrl = TextEditingController();

  // Boundary
  List<LatLng> _boundaryPoints = [];
  LatLng? _centerPoint;

  @override
  void dispose() {
    for (final c in [
      _nameCtrl,
      _villageCtrl,
      _talukaCtrl,
      _districtCtrl,
      _stateCtrl,
      _areaCtrl,
      _cropCtrl,
      _seasonCtrl,
      _khasraCtrl,
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  bool get _hasBoundary => _boundaryPoints.length >= 3;

  String _getErrorMessage(Object error) {
    if (error is DioException) {
      final responseData = error.response?.data;
      if (responseData is Map<String, dynamic>) {
        final detail = responseData['detail'];
        if (detail is String && detail.isNotEmpty) {
          return detail;
        }
        final message = responseData['message'];
        if (message is String && message.isNotEmpty) {
          return message;
        }
      }
      return error.message ?? 'Something went wrong';
    }
    return error.toString();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (!_hasBoundary) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(AppLocalizations.of(context)!.boundaryRequired),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final coords =
        _boundaryPoints.map((p) => [p.latitude, p.longitude]).toList();

    final center = _centerPoint ??
        LatLng(
          _boundaryPoints.map((p) => p.latitude).reduce((a, b) => a + b) /
              _boundaryPoints.length,
          _boundaryPoints.map((p) => p.longitude).reduce((a, b) => a + b) /
              _boundaryPoints.length,
        );

    final payload = {
      'name': _nameCtrl.text.trim(),
      'village': _villageCtrl.text.trim(),
      if (_talukaCtrl.text.isNotEmpty) 'taluka': _talukaCtrl.text.trim(),
      'district': _districtCtrl.text.trim(),
      'state': _stateCtrl.text.trim(),
      'area_acres': double.parse(_areaCtrl.text.trim()),
      'crop_type': _cropCtrl.text.trim(),
      'season': _seasonCtrl.text.trim(),
      if (_khasraCtrl.text.isNotEmpty) 'khasra_number': _khasraCtrl.text.trim(),
      'boundary': {
        'coordinates': coords,
        'center_lat': center.latitude,
        'center_lng': center.longitude,
        'geojson': '',
      },
    };

    final farm =
        await ref.read(createFarmProvider.notifier).createFarm(payload);
    final state = ref.read(createFarmProvider);

    if (!mounted) return;

    if (state.hasError || farm == null) {
      final errorMessage = state.error != null
          ? _getErrorMessage(state.error!)
          : 'Unable to submit farm details';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(errorMessage),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(AppLocalizations.of(context)!.farmRegistered),
        backgroundColor: AppColors.success,
      ),
    );
    context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final createState = ref.watch(createFarmProvider);
    final isLoading = createState.isLoading;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(l10n.registerFarm),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => context.pop(),
        ),
      ),
      body: Form(
        key: _formKey,
        child: Stepper(
          currentStep: _currentStep,
          type: StepperType.vertical,
          physics: const ClampingScrollPhysics(),
          onStepContinue: () async {
            if (_currentStep == 0) {
              // Validate step 1 fields
              if (_nameCtrl.text.isEmpty ||
                  _villageCtrl.text.isEmpty ||
                  _districtCtrl.text.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                      content: Text('Please fill all required fields')),
                );
                return;
              }
              setState(() => _currentStep = 1);
            } else if (_currentStep == 1) {
              if (_areaCtrl.text.isEmpty ||
                  _cropCtrl.text.isEmpty ||
                  _seasonCtrl.text.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                      content: Text('Please fill all required fields')),
                );
                return;
              }
              setState(() => _currentStep = 2);
            } else {
              await _submit();
            }
          },
          onStepCancel: () {
            if (_currentStep > 0) setState(() => _currentStep--);
          },
          controlsBuilder: (context, details) {
            final isLast = _currentStep == 2;
            return Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Row(
                children: [
                  Expanded(
                    child: AppButton(
                      label: isLast ? l10n.submit : l10n.next,
                      onPressed: isLoading ? null : details.onStepContinue,
                      isLoading: isLoading && isLast,
                      icon: isLast
                          ? Icons.check_rounded
                          : Icons.arrow_forward_rounded,
                    ),
                  ),
                  if (_currentStep > 0) ...[
                    const SizedBox(width: 12),
                    Expanded(
                      child: AppButton(
                        label: l10n.back,
                        variant: AppButtonVariant.outlined,
                        onPressed: details.onStepCancel,
                      ),
                    ),
                  ],
                ],
              ),
            );
          },
          steps: [
            // Step 1 — Farm Location Details
            Step(
              title: Text(l10n.village,
                  style: const TextStyle(fontWeight: FontWeight.w600)),
              subtitle: const Text('Location & identity'),
              isActive: _currentStep >= 0,
              state: _currentStep > 0 ? StepState.complete : StepState.indexed,
              content: Column(
                children: [
                  AppTextField(
                    label: l10n.farmName,
                    hint: l10n.farmNameHint,
                    controller: _nameCtrl,
                    textCapitalization: TextCapitalization.words,
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? l10n.farmNameRequired
                        : null,
                  ),
                  const SizedBox(height: 12),
                  AppTextField(
                    label: l10n.village,
                    hint: l10n.villageHint,
                    controller: _villageCtrl,
                    textCapitalization: TextCapitalization.words,
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? l10n.villageRequired
                        : null,
                  ),
                  const SizedBox(height: 12),
                  AppTextField(
                    label: 'Taluka (optional)',
                    hint: 'Enter taluka',
                    controller: _talukaCtrl,
                    textCapitalization: TextCapitalization.words,
                  ),
                  const SizedBox(height: 12),
                  AppTextField(
                    label: l10n.district,
                    hint: l10n.districtHint,
                    controller: _districtCtrl,
                    textCapitalization: TextCapitalization.words,
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? l10n.districtRequired
                        : null,
                  ),
                  const SizedBox(height: 12),
                  AppTextField(
                    label: l10n.state,
                    hint: 'State',
                    controller: _stateCtrl,
                    textCapitalization: TextCapitalization.words,
                  ),
                  const SizedBox(height: 12),
                  AppTextField(
                    label: l10n.khasraNumber,
                    hint: 'e.g. KH-1234',
                    controller: _khasraCtrl,
                  ),
                ],
              ),
            ),

            // Step 2 — Crop Details
            Step(
              title: Text(l10n.cropType,
                  style: const TextStyle(fontWeight: FontWeight.w600)),
              subtitle: const Text('Crop & season info'),
              isActive: _currentStep >= 1,
              state: _currentStep > 1 ? StepState.complete : StepState.indexed,
              content: Column(
                children: [
                  AppTextField(
                    label: l10n.areaAcres,
                    hint: l10n.areaHint,
                    controller: _areaCtrl,
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                    inputFormatters: [
                      FilteringTextInputFormatter.allow(
                          RegExp(r'^\d*\.?\d{0,3}')),
                    ],
                    validator: (v) {
                      if (v == null || v.isEmpty) return l10n.areaRequired;
                      final d = double.tryParse(v);
                      if (d == null || d <= 0) return 'Enter a valid area';
                      return null;
                    },
                  ),
                  const SizedBox(height: 12),
                  AppTextField(
                    label: l10n.cropType,
                    hint: l10n.cropTypeHint,
                    controller: _cropCtrl,
                    textCapitalization: TextCapitalization.words,
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? l10n.cropTypeRequired
                        : null,
                  ),
                  const SizedBox(height: 12),
                  AppTextField(
                    label: l10n.season,
                    hint: l10n.seasonHint,
                    controller: _seasonCtrl,
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? l10n.seasonRequired
                        : null,
                  ),
                ],
              ),
            ),

            // Step 3 — Boundary Map
            Step(
              title: Text(l10n.drawBoundary,
                  style: const TextStyle(fontWeight: FontWeight.w600)),
              subtitle: const Text('Tap on map to mark boundary'),
              isActive: _currentStep >= 2,
              state: _hasBoundary ? StepState.complete : StepState.indexed,
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (_hasBoundary)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                      margin: const EdgeInsets.only(bottom: 12),
                      decoration: BoxDecoration(
                        color: AppColors.success.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                            color: AppColors.success.withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle_rounded,
                              color: AppColors.success, size: 16),
                          const SizedBox(width: 8),
                          Text(
                            l10n.boundaryPoints(_boundaryPoints.length),
                            style: const TextStyle(
                              color: AppColors.success,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  BoundaryMapWidget(
                    initialPoints: _boundaryPoints,
                    onBoundaryChanged: (points) {
                      setState(() {
                        _boundaryPoints = points;

                        if (points.isNotEmpty) {
                          _centerPoint = LatLng(
                            points.map((p) => p.latitude).reduce((a, b) => a + b) /
                                points.length,
                            points.map((p) => p.longitude).reduce((a, b) => a + b) /
                                points.length,
                          );
                        }
                      });
                    },
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Tap on the map to add boundary points. Add at least 3 points.',
                    style: Theme.of(context).textTheme.bodySmall,
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
