class CropHealthEntity {
  final String farmId;
  final int? healthScore;
  final String? healthClass;
  final int totalImages;
  final int analyzedImages;
  final Map<String, dynamic> diseaseSummary;
  final String? lastAnalyzed;
  final String? message;

  const CropHealthEntity({
    required this.farmId,
    this.healthScore,
    this.healthClass,
    required this.totalImages,
    required this.analyzedImages,
    required this.diseaseSummary,
    this.lastAnalyzed,
    this.message,
  });

  bool get hasData => healthScore != null;

  factory CropHealthEntity.fromJson(Map<String, dynamic> json) =>
      CropHealthEntity(
        farmId: json['farm_id'] as String,
        healthScore: json['health_score'] as int?,
        healthClass: json['health_class'] as String?,
        totalImages: json['total_images'] as int? ?? 0,
        analyzedImages: json['analyzed_images'] as int? ?? 0,
        diseaseSummary:
            (json['disease_summary'] as Map<String, dynamic>?) ?? {},
        lastAnalyzed: json['last_analyzed'] as String?,
        message: json['message'] as String?,
      );
}