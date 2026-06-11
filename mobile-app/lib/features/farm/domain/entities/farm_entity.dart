class FarmBoundaryEntity {
  final List<List<double>> coordinates;
  final double centerLat;
  final double centerLng;
  final String geojson;

  const FarmBoundaryEntity({
    required this.coordinates,
    required this.centerLat,
    required this.centerLng,
    required this.geojson,
  });

  factory FarmBoundaryEntity.fromJson(Map<String, dynamic> json) {
    final rawCoords = json['coordinates'] as List<dynamic>;
    return FarmBoundaryEntity(
      coordinates: rawCoords
          .map((e) =>
              (e as List<dynamic>).map((v) => (v as num).toDouble()).toList())
          .toList(),
      centerLat: (json['center_lat'] as num).toDouble(),
      centerLng: (json['center_lng'] as num).toDouble(),
      geojson: json['geojson'] as String,
    );
  }
}

class FarmEntity {
  final String id;
  final String ownerId;
  final String name;
  final String village;
  final String? taluka;
  final String district;
  final String state;
  final double areaAcres;
  final String cropType;
  final String season;
  final String? khasraNumber;
  final bool isActive;
  final FarmBoundaryEntity? boundary;
  final DateTime createdAt;

  const FarmEntity({
    required this.id,
    required this.ownerId,
    required this.name,
    required this.village,
    this.taluka,
    required this.district,
    required this.state,
    required this.areaAcres,
    required this.cropType,
    required this.season,
    this.khasraNumber,
    required this.isActive,
    this.boundary,
    required this.createdAt,
  });

  factory FarmEntity.fromJson(Map<String, dynamic> json) => FarmEntity(
        id: json['id'] as String,
        ownerId: json['owner_id'] as String,
        name: json['name'] as String,
        village: json['village'] as String,
        taluka: json['taluka'] as String?,
        district: json['district'] as String,
        state: json['state'] as String,
        areaAcres: (json['area_acres'] as num).toDouble(),
        cropType: json['crop_type'] as String,
        season: json['season'] as String,
        khasraNumber: json['khasra_number'] as String?,
        isActive: json['is_active'] as bool? ?? true,
        boundary: json['boundary'] != null
            ? FarmBoundaryEntity.fromJson(
                json['boundary'] as Map<String, dynamic>)
            : null,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}
