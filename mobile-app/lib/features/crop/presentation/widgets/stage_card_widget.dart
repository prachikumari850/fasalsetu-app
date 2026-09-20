import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:geolocator/geolocator.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:fasalsetu/l10n/app_localizations.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/features/crop/domain/entities/crop_entities.dart';
import 'package:fasalsetu/features/crop/presentation/providers/crop_provider.dart';

class StageCardWidget extends ConsumerStatefulWidget {
  final TimelineStageEntity timelineStage;
  final String farmId;
  final int stageIndex;
  final bool showConnector; 

  const StageCardWidget({
    super.key,
    required this.timelineStage,
    required this.farmId,
    required this.stageIndex,
    required this.showConnector,
  });

  @override
  ConsumerState<StageCardWidget> createState() => _StageCardWidgetState();
}

class _StageCardWidgetState extends ConsumerState<StageCardWidget> {
  bool _uploading = false;
  bool _expanded = false;

  Future<bool> _confirmUpload(XFile picked) async {
    final bytes = await picked.readAsBytes();
    if (!mounted) return false;
    return await showDialog<bool>(
          context: context,
          builder: (dialogContext) => AlertDialog(
            title: const Text('Upload this photo?'),
            content: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.memory(bytes, fit: BoxFit.cover),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext, false),
                child: const Text('Choose another'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(dialogContext, true),
                child: const Text('Upload'),
              ),
            ],
          ),
        ) ??
        false;
  }

  String _stageLabel(CropStageName stage, AppLocalizations l10n) {
    switch (stage) {
      case CropStageName.sowing:
        return l10n.sowing;
      case CropStageName.germination:
        return l10n.germination;
      case CropStageName.vegetative:
        return l10n.vegetative;
      case CropStageName.flowering:
        return l10n.flowering;
      case CropStageName.preHarvest:
        return l10n.preHarvest;
    }
  }

  IconData _stageIcon(CropStageName stage) {
    switch (stage) {
      case CropStageName.sowing:
        return Icons.grass_rounded;
      case CropStageName.germination:
        return Icons.eco_rounded;
      case CropStageName.vegetative:
        return Icons.park_rounded;
      case CropStageName.flowering:
        return Icons.local_florist_rounded;
      case CropStageName.preHarvest:
        return Icons.agriculture_rounded;
    }
  }

  Color _stageColor(int index) {
    const colors = [
      Color(0xFF795548), // Sowing - brown
      Color(0xFF4CAF50), // Germination - green
      Color(0xFF2E7D32), // Vegetative - dark green
      Color(0xFFE91E63), // Flowering - pink
      Color(0xFFF9A825), // Pre-harvest - amber
    ];
    return colors[index % colors.length];
  }

  Future<void> _pickAndUpload(ImageSource source) async {
    final l10n = AppLocalizations.of(context)!;
    // Invoke the browser picker immediately from the tap callback. Awaiting
    // geolocation first loses the Web user-activation required by browsers.
    final picker = ImagePicker();
    final picked = await picker.pickImage(
      source: source,
      imageQuality: 85,
      maxWidth: 1920,
      maxHeight: 1920,
    );
    if (picked == null) return;

    try {
      if (!await _confirmUpload(picked)) return;
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('The selected image could not be read. Please choose another image.'),
          backgroundColor: AppColors.error,
        ));
      }
      return;
    }

    setState(() => _uploading = true);

    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        throw StateError(l10n.gpsRequired);
      }

      // Get current position
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      final imageBytes = await picked.readAsBytes();
      final uploadError = await ref
          .read(cropTimelineProvider(widget.farmId).notifier)
          .uploadImage(
            farmId: widget.farmId,
            stageName: widget.timelineStage.stage.stageName,
            imageBytes: imageBytes,
            fileName: picked.name.isEmpty ? 'crop_photo.jpg' : picked.name,
            mimeType: picked.mimeType,
            latitude: position.latitude,
            longitude: position.longitude,
          );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              uploadError ?? l10n.photoUploaded,
            ),
            backgroundColor:
                uploadError == null ? AppColors.success : AppColors.error,
          ),
        );
      }
    } catch (e) {
      // Surface the REAL error instead of a silent generic failure.
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Upload failed: $e'),
            backgroundColor: AppColors.error,
            duration: const Duration(seconds: 6),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  void _showImageSourceSheet() {
    final l10n = AppLocalizations.of(context)!;
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: 12),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.camera_alt_rounded,
                      color: AppColors.primary),
                ),
                title: Text(l10n.takePhoto),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickAndUpload(ImageSource.camera);
                },
              ),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppColors.info.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.photo_library_rounded,
                      color: AppColors.info),
                ),
                title: Text(l10n.chooseFromGallery),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickAndUpload(ImageSource.gallery);
                },
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _markComplete() async {
    final l10n = AppLocalizations.of(context)!;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Text(l10n.stageCompleted),
        content: Text(
          'Mark ${_stageLabel(widget.timelineStage.stage.stageName, l10n)} as complete?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(l10n.cancel),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(
              l10n.continueText,
              style: const TextStyle(color: AppColors.primary),
            ),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await ref.read(cropTimelineProvider(widget.farmId).notifier).markComplete(
            farmId: widget.farmId,
            stageId: widget.timelineStage.stage.id,
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final stage = widget.timelineStage.stage;
    final images = widget.timelineStage.images;
    final color = _stageColor(widget.stageIndex);
    final isCompleted = stage.isCompleted;

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Timeline connector
          Column(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: isCompleted ? color : AppColors.surfaceVariant,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isCompleted ? color : AppColors.border,
                    width: 2,
                  ),
                ),
                child: Icon(
                  isCompleted
                      ? Icons.check_rounded
                      : _stageIcon(stage.stageName),
                  size: 18,
                  color: isCompleted ? Colors.white : color,
                ),
              ),
              if (widget.showConnector)
                Expanded(
                  child: Container(
                    width: 2,
                    color:
                        isCompleted ? color.withValues(alpha: 0.4) : AppColors.border,
                  ),
                ),
            ],
          ),

          const SizedBox(width: 12),

          // Card
          Expanded(
            child: Card(
              margin: const EdgeInsets.only(bottom: 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Stage header
                  InkWell(
                    onTap: () => setState(() => _expanded = !_expanded),
                    borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: color.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Icon(_stageIcon(stage.stageName),
                                color: color, size: 18),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _stageLabel(stage.stageName, l10n),
                                  style: Theme.of(context)
                                      .textTheme
                                      .titleMedium
                                      ?.copyWith(fontWeight: FontWeight.w600),
                                ),
                                if (stage.imageCount > 0)
                                  Text(
                                    '${stage.imageCount} photo${stage.imageCount > 1 ? 's' : ''}',
                                    style:
                                        Theme.of(context).textTheme.bodySmall,
                                  ),
                              ],
                            ),
                          ),
                          if (isCompleted)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: AppColors.success.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Text(
                                '✓ Done',
                                style: TextStyle(
                                  color: AppColors.success,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          const SizedBox(width: 4),
                          Icon(
                            _expanded
                                ? Icons.keyboard_arrow_up_rounded
                                : Icons.keyboard_arrow_down_rounded,
                            color: AppColors.textHint,
                            size: 20,
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Expanded content
                  if (_expanded) ...[
                    const Divider(height: 1),
                    Padding(
                      padding: const EdgeInsets.all(14),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Image thumbnails
                          if (images.isNotEmpty) ...[
                            SizedBox(
                              height: 80,
                              child: ListView.separated(
                                scrollDirection: Axis.horizontal,
                                itemCount: images.length,
                                separatorBuilder: (_, __) =>
                                    const SizedBox(width: 8),
                                itemBuilder: (context, i) => _ImageThumbnail(
                                  image: images[i],
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                          ],

                          // Upload button
                          if (!isCompleted)
                            Row(
                              children: [
                                Expanded(
                                  child: OutlinedButton.icon(
                                    onPressed: _uploading
                                        ? null
                                        : _showImageSourceSheet,
                                    icon: _uploading
                                        ? const SizedBox(
                                            width: 14,
                                            height: 14,
                                            child: CircularProgressIndicator(
                                              strokeWidth: 2,
                                              color: AppColors.primary,
                                            ),
                                          )
                                        : const Icon(
                                            Icons.add_a_photo_rounded,
                                            size: 16,
                                          ),
                                    label: Text(
                                      _uploading
                                          ? 'Uploading...'
                                          : l10n.uploadPhoto,
                                    ),
                                    style: OutlinedButton.styleFrom(
                                      foregroundColor: AppColors.primary,
                                      side: const BorderSide(
                                          color: AppColors.primary),
                                      minimumSize: const Size(0, 40),
                                    ),
                                  ),
                                ),
                                if (images.isNotEmpty) ...[
                                  const SizedBox(width: 8),
                                  IconButton(
                                    onPressed: _markComplete,
                                    icon: const Icon(
                                      Icons.check_circle_outline_rounded,
                                      color: AppColors.success,
                                    ),
                                    tooltip: l10n.stageCompleted,
                                    style: IconButton.styleFrom(
                                      backgroundColor:
                                          AppColors.success.withValues(alpha: 0.1),
                                    ),
                                  ),
                                ],
                              ],
                            ),

                          // GPS warning
                          if (images.any((img) => !img.isInsideFence)) ...[
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                color: AppColors.warning.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                    color: AppColors.warning.withValues(alpha: 0.3)),
                              ),
                              child: const Row(
                                children: [
                                  Icon(Icons.warning_amber_rounded,
                                      size: 14, color: AppColors.warning),
                                  SizedBox(width: 6),
                                  Expanded(
                                    child: Text(
                                      'Some photos were taken outside the farm boundary',
                                      style: TextStyle(
                                        fontSize: 11,
                                        color: AppColors.warning,
                                        fontFamily: 'NotoSansDevanagari',
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ImageThumbnail extends StatelessWidget {
  final CropImageEntity image;
  const _ImageThumbnail({required this.image});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.push(
        '/farms/${image.farmId}/analysis/${image.id}',
      ),
      child: Stack(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: CachedNetworkImage(
              imageUrl: image.storageUrl,
              width: 80,
              height: 80,
              fit: BoxFit.cover,
              placeholder: (_, __) => Container(
                color: AppColors.surfaceVariant,
                child: const Icon(Icons.image_outlined,
                    color: AppColors.textHint),
              ),
              errorWidget: (_, __, ___) => Container(
                color: AppColors.surfaceVariant,
                child: const Icon(Icons.broken_image_outlined,
                    color: AppColors.textHint),
              ),
            ),
          ),
          Positioned(
            bottom: 4,
            left: 4,
            child: Container(
              padding: const EdgeInsets.all(3),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.5),
                shape: BoxShape.circle,
              ),
              child: Icon(
                image.aiProcessed
                    ? Icons.check_circle_rounded
                    : Icons.hourglass_bottom_rounded,
                size: 10,
                color: image.aiProcessed ? AppColors.success : Colors.white,
              ),
            ),
          ),
          if (!image.isInsideFence)
            Positioned(
              top: 4,
              right: 4,
              child: Container(
                width: 16,
                height: 16,
                decoration: const BoxDecoration(
                  color: AppColors.warning,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.warning_rounded,
                  size: 10,
                  color: Colors.white,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
