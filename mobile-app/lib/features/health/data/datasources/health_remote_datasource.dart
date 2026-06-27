import 'package:dio/dio.dart';
import 'package:fasalsetu/features/health/domain/entities/health_entities.dart';

class HealthRemoteDataSource {
  final Dio _dio;
  HealthRemoteDataSource(this._dio);

  Future<CropHealthEntity> getFarmHealth(String farmId) async {
    final response = await _dio.get('/crops/$farmId/health');
    return CropHealthEntity.fromJson(
      response.data['data'] as Map<String, dynamic>,
    );
  }
}