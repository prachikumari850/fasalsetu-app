import 'package:dio/dio.dart';
import 'package:fasalsetu/features/analysis/domain/entities/analysis_entities.dart';

class AnalysisRemoteDataSource {
  final Dio _dio;
  AnalysisRemoteDataSource(this._dio);

  Future<ImageAnalysisEntity> getImageAnalysis({
    required String farmId,
    required String imageId,
  }) async {
    final response = await _dio.get('/crops/$farmId/analysis/$imageId');
    return ImageAnalysisEntity.fromJson(
      response.data['data'] as Map<String, dynamic>,
    );
  }
}