class TrustScoreEntity {
  final String farmId;
  final double? score;
  final String? grade;
  final Map<String, dynamic>? breakdown;
  final String? calculatedAt;
  final String? message;

  const TrustScoreEntity({
    required this.farmId,
    this.score,
    this.grade,
    this.breakdown,
    this.calculatedAt,
    this.message,
  });

  bool get hasScore => score != null;

  factory TrustScoreEntity.fromJson(Map<String, dynamic> json) =>
      TrustScoreEntity(
        farmId: json['farm_id'] as String,
        score: (json['score'] as num?)?.toDouble(),
        grade: json['grade'] as String?,
        breakdown: json['breakdown'] as Map<String, dynamic>?,
        calculatedAt: json['calculated_at'] as String?,
        message: json['message'] as String?,
      );
}