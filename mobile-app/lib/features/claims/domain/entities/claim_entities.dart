// class ClaimSummary {
//   final String id;
//   final String farmId;
//   final String status;
//   final String damageType;
//   final double? trustScore;
//   final String? submittedAt;

//   ClaimSummary({
//     required this.id,
//     required this.farmId,
//     required this.status,
//     required this.damageType,
//     this.trustScore,
//     this.submittedAt,
//   });

//   factory ClaimSummary.fromJson(Map<String, dynamic> json) => ClaimSummary(
//         id: json['id'] as String,
//         farmId: json['farm_id'] as String,
//         status: json['status'] as String,
//         damageType: json['damage_type'] as String,
//         trustScore: (json['trust_score'] as num?)?.toDouble(),
//         submittedAt: json['submitted_at'] as String?,
//       );
// }

// class ClaimDetail extends ClaimSummary {
//   final String? damageDescription;
//   final double? estimatedLoss;
//   final double? affectedAcres;
//   final bool fraudAnalyzed;
//   final double? fraudScore;
//   final List<String> fraudFlags;
//   final String? officerNotes;

//   ClaimDetail({
//     required super.id,
//     required super.farmId,
//     required super.status,
//     required super.damageType,
//     super.trustScore,
//     super.submittedAt,
//     this.damageDescription,
//     this.estimatedLoss,
//     this.affectedAcres,
//     required this.fraudAnalyzed,
//     this.fraudScore,
//     required this.fraudFlags,
//     this.officerNotes,
//   });

//   factory ClaimDetail.fromJson(Map<String, dynamic> json) => ClaimDetail(
//         id: json['id'] as String,
//         farmId: json['farm_id'] as String,
//         status: json['status'] as String,
//         damageType: json['damage_type'] as String,
//         trustScore: (json['trust_score'] as num?)?.toDouble(),
//         submittedAt: json['submitted_at'] as String?,
//         damageDescription: json['damage_description'] as String?,
//         estimatedLoss: (json['estimated_loss'] as num?)?.toDouble(),
//         affectedAcres: (json['affected_acres'] as num?)?.toDouble(),
//         fraudAnalyzed: json['fraud_analyzed'] as bool? ?? false,
//         fraudScore: (json['fraud_score'] as num?)?.toDouble(),
//         fraudFlags: (json['fraud_flags'] as List?)?.cast<String>() ?? [],
//         officerNotes: json['officer_notes'] as String?,
//       );
// }

class ClaimSummary {
  final String id;
  final String farmId;
  final String status;
  final String damageType;
  final double? trustScore;
  final String? submittedAt;

  ClaimSummary({
    required this.id,
    required this.farmId,
    required this.status,
    required this.damageType,
    this.trustScore,
    this.submittedAt,
  });

  factory ClaimSummary.fromJson(Map<String, dynamic> json) => ClaimSummary(
        id: json['id'] as String,
        farmId: json['farm_id'] as String,
        status: json['status'] as String,
        damageType: json['damage_type'] as String,
        trustScore: (json['trust_score'] as num?)?.toDouble(),
        submittedAt: json['submitted_at'] as String?,
      );
}

class ClaimDetail extends ClaimSummary {
  final String farmerId;
  final String? damageDescription;
  final double? estimatedLoss;
  final double? affectedAcres;
  final String? reviewedAt;
  final String? officerNotes;
  final bool fraudAnalyzed;
  final double? fraudScore;
  final List<String> fraudFlags;

  ClaimDetail({
    required super.id,
    required super.farmId,
    required super.status,
    required super.damageType,
    super.trustScore,
    super.submittedAt,
    required this.farmerId,
    this.damageDescription,
    this.estimatedLoss,
    this.affectedAcres,
    this.reviewedAt,
    this.officerNotes,
    required this.fraudAnalyzed,
    this.fraudScore,
    required this.fraudFlags,
  });

  factory ClaimDetail.fromJson(Map<String, dynamic> json) => ClaimDetail(
        id: json['id'] as String,
        farmId: json['farm_id'] as String,
        farmerId: json['farmer_id'] as String,
        status: json['status'] as String,
        damageType: json['damage_type'] as String,
        trustScore: (json['trust_score'] as num?)?.toDouble(),
        submittedAt: json['submitted_at'] as String?,
        damageDescription: json['damage_description'] as String?,
        estimatedLoss: (json['estimated_loss'] as num?)?.toDouble(),
        affectedAcres: (json['affected_acres'] as num?)?.toDouble(),
        reviewedAt: json['reviewed_at'] as String?,
        officerNotes: json['officer_notes'] as String?,
        fraudAnalyzed: json['fraud_analyzed'] as bool? ?? false,
        fraudScore: (json['fraud_score'] as num?)?.toDouble(),
        fraudFlags: (json['fraud_flags'] as List?)?.cast<String>() ?? [],
      );
}

class ClaimCreateRequest {
  final String farmId;
  final String damageType;
  final String? damageDescription;
  final double? estimatedLoss;
  final double? affectedAcres;

  ClaimCreateRequest({
    required this.farmId,
    required this.damageType,
    this.damageDescription,
    this.estimatedLoss,
    this.affectedAcres,
  });

  Map<String, dynamic> toJson() => {
        'farm_id': farmId,
        'damage_type': damageType,
        if (damageDescription != null) 'damage_description': damageDescription,
        if (estimatedLoss != null) 'estimated_loss': estimatedLoss,
        if (affectedAcres != null) 'affected_acres': affectedAcres,
      };
}