class AdvisoryEntity {
  final String id;
  final String farmId;
  final String? diseaseReportId;
  final String titleEn;
  final String titleHi;
  final String bodyEn;
  final String bodyHi;
  final String priority;
  final bool isRead;
  final String createdAt;

  AdvisoryEntity({
    required this.id,
    required this.farmId,
    this.diseaseReportId,
    required this.titleEn,
    required this.titleHi,
    required this.bodyEn,
    required this.bodyHi,
    required this.priority,
    required this.isRead,
    required this.createdAt,
  });

  factory AdvisoryEntity.fromJson(Map<String, dynamic> json) => AdvisoryEntity(
        id: json['id'] as String,
        farmId: json['farm_id'] as String,
        diseaseReportId: json['disease_report_id'] as String?,
        titleEn: json['title_en'] as String,
        titleHi: json['title_hi'] as String,
        bodyEn: json['body_en'] as String,
        bodyHi: json['body_hi'] as String,
        priority: json['priority'] as String,
        isRead: json['is_read'] as bool? ?? false,
        createdAt: json['created_at'] as String,
      );
}