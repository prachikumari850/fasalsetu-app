enum CropStageName {
  sowing,
  germination,
  vegetative,
  flowering,
  preHarvest;

  String get value {
    switch (this) {
      case CropStageName.sowing:
        return 'sowing';
      case CropStageName.germination:
        return 'germination';
      case CropStageName.vegetative:
        return 'vegetative';
      case CropStageName.flowering:
        return 'flowering';
      case CropStageName.preHarvest:
        return 'pre_harvest';
    }
  }

  static CropStageName fromValue(String value) {
    switch (value) {
      case 'sowing':
        return CropStageName.sowing;
      case 'germination':
        return CropStageName.germination;
      case 'vegetative':
        return CropStageName.vegetative;
      case 'flowering':
        return CropStageName.flowering;
      case 'pre_harvest':
        return CropStageName.preHarvest;
      default:
        return CropStageName.sowing;
    }
  }
}

class CropImageEntity {
  final String id;
  final String farmId;
  final String? stageId;
  final String storageUrl;
  final double latitude;
  final double longitude;
  final bool isInsideFence;
  final bool aiProcessed;
  final DateTime capturedAt;

  const CropImageEntity({
    required this.id,
    required this.farmId,
    this.stageId,
    required this.storageUrl,
    required this.latitude,
    required this.longitude,
    required this.isInsideFence,
    required this.aiProcessed,
    required this.capturedAt,
  });

  factory CropImageEntity.fromJson(Map<String, dynamic> json) =>
      CropImageEntity(
        id: json['id'] as String,
        farmId: json['farm_id'] as String,
        stageId: json['stage_id'] as String?,
        storageUrl: json['storage_url'] as String,
        latitude: (json['latitude'] as num).toDouble(),
        longitude: (json['longitude'] as num).toDouble(),
        isInsideFence: json['is_inside_fence'] as bool? ?? false,
        aiProcessed: json['ai_processed'] as bool? ?? false,
        capturedAt: DateTime.parse(json['captured_at'] as String),
      );
}

class CropStageEntity {
  final String id;
  final String farmId;
  final CropStageName stageName;
  final DateTime? expectedDate;
  final DateTime? actualDate;
  final String? notes;
  final bool isCompleted;
  final int imageCount;

  const CropStageEntity({
    required this.id,
    required this.farmId,
    required this.stageName,
    this.expectedDate,
    this.actualDate,
    this.notes,
    required this.isCompleted,
    required this.imageCount,
  });

  factory CropStageEntity.fromJson(Map<String, dynamic> json) =>
      CropStageEntity(
        id: json['id'] as String,
        farmId: json['farm_id'] as String,
        stageName: CropStageName.fromValue(json['stage_name'] as String),
        expectedDate: json['expected_date'] != null
            ? DateTime.parse(json['expected_date'] as String)
            : null,
        actualDate: json['actual_date'] != null
            ? DateTime.parse(json['actual_date'] as String)
            : null,
        notes: json['notes'] as String?,
        isCompleted: json['is_completed'] as bool? ?? false,
        imageCount: json['image_count'] as int? ?? 0,
      );
}

class TimelineStageEntity {
  final CropStageEntity stage;
  final List<CropImageEntity> images;

  const TimelineStageEntity({
    required this.stage,
    required this.images,
  });

  factory TimelineStageEntity.fromJson(Map<String, dynamic> json) =>
      TimelineStageEntity(
        stage: CropStageEntity.fromJson(json['stage'] as Map<String, dynamic>),
        images: (json['images'] as List<dynamic>)
            .map((e) => CropImageEntity.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class CropTimelineEntity {
  final String farmId;
  final List<TimelineStageEntity> stages;
  final int totalImages;
  final int completedStages;

  const CropTimelineEntity({
    required this.farmId,
    required this.stages,
    required this.totalImages,
    required this.completedStages,
  });

  factory CropTimelineEntity.fromJson(Map<String, dynamic> json) =>
      CropTimelineEntity(
        farmId: json['farm_id'] as String,
        stages: (json['stages'] as List<dynamic>)
            .map((e) => TimelineStageEntity.fromJson(e as Map<String, dynamic>))
            .toList(),
        totalImages: json['total_images'] as int? ?? 0,
        completedStages: json['completed_stages'] as int? ?? 0,
      );
}
