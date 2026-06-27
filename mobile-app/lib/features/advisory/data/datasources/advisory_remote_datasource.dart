import 'package:dio/dio.dart';
import 'package:fasalsetu/features/advisory/domain/entities/advisory_entities.dart';

class AdvisoryRemoteDataSource {
  final Dio _dio;
  AdvisoryRemoteDataSource(this._dio);

  Future<List<AdvisoryEntity>> getAdvisories(
    String farmId, {
    bool unreadOnly = false,
  }) async {
    final response = await _dio.get(
      '/advisories/$farmId',
      queryParameters: {'unread_only': unreadOnly},
    );
    final data = response.data['data'] as List;
    return data
        .map((j) => AdvisoryEntity.fromJson(j as Map<String, dynamic>))
        .toList();
  }

  Future<AdvisoryEntity> markRead(String advisoryId) async {
    final response = await _dio.put('/advisories/$advisoryId/read');
    return AdvisoryEntity.fromJson(response.data['data'] as Map<String, dynamic>);
  }
}