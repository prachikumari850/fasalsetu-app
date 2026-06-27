class DiseaseReportEntity {
  final String id;
  final String diseaseName;
  final double confidence;
  final String severity;
  final Map<String, dynamic>? bboxData;
  final Map<String, dynamic>? rawOutput;
  final String detectedAt;

  const DiseaseReportEntity({
    required this.id,
    required this.diseaseName,
    required this.confidence,
    required this.severity,
    this.bboxData,
    this.rawOutput,
    required this.detectedAt,
  });

  factory DiseaseReportEntity.fromJson(Map<String, dynamic> json) =>
      DiseaseReportEntity(
        id: json['id'] as String,
        diseaseName: json['disease_name'] as String,
        confidence: (json['confidence'] as num).toDouble(),
        severity: json['severity'] as String,
        bboxData: json['bbox_data'] as Map<String, dynamic>?,
        rawOutput: json['raw_output'] as Map<String, dynamic>?,
        detectedAt: json['detected_at'] as String,
      );
}

class ImageAnalysisEntity {
  final String imageId;
  final bool aiProcessed;
  final bool isInsideFence;
  final List<DiseaseReportEntity> reports;

  const ImageAnalysisEntity({
    required this.imageId,
    required this.aiProcessed,
    required this.isInsideFence,
    required this.reports,
  });

  factory ImageAnalysisEntity.fromJson(Map<String, dynamic> json) =>
      ImageAnalysisEntity(
        imageId: json['image_id'] as String,
        aiProcessed: json['ai_processed'] as bool? ?? false,
        isInsideFence: json['is_inside_fence'] as bool? ?? false,
        reports: (json['reports'] as List<dynamic>? ?? [])
            .map((e) => DiseaseReportEntity.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}