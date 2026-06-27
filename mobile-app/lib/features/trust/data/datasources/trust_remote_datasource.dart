import 'package:dio/dio.dart';
import 'package:fasalsetu/features/trust/domain/entities/trust_entities.dart';

class TrustRemoteDataSource {
  final Dio _dio;
  TrustRemoteDataSource(this._dio);

  Future<TrustScoreEntity> getTrustScore(String farmId) async {
    final response = await _dio.get('/fraud/trust/$farmId');
    return TrustScoreEntity.fromJson(
      response.data['data'] as Map<String, dynamic>,
    );
  }
}