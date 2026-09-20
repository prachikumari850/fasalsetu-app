import 'package:dio/dio.dart';
import 'package:fasalsetu/features/crop/domain/entities/crop_entities.dart';

class CropRemoteDataSource {
  final Dio _dio;
  CropRemoteDataSource(this._dio);

  Future<CropTimelineEntity> getTimeline(String farmId) async {
    final response = await _dio.get('/crops/$farmId/timeline');
    return CropTimelineEntity.fromJson(
      response.data['data'] as Map<String, dynamic>,
    );
  }

  Future<CropImageEntity> uploadImage({
    required String farmId,
    required CropStageName stageName,
    required List<int> imageBytes,
    required String fileName,
    required String? mimeType,
    required double latitude,
    required double longitude,
    required DateTime capturedAt,
  }) async {
    final formData = FormData.fromMap({
      'farm_id': farmId,
      'stage_name': stageName.value,
      'latitude': latitude.toString(),
      'longitude': longitude.toString(),
      'captured_at': capturedAt.toIso8601String(),
      // XFile.path is a browser blob URL on Flutter Web, not a filesystem path.
      // Upload the bytes so the same request works on web and mobile.
      'file': MultipartFile.fromBytes(
        imageBytes,
        filename: fileName,
        contentType: DioMediaType.parse(mimeType ?? 'image/jpeg'),
      ),
    });

    final response = await _dio.post(
      '/images/upload',
      data: formData,
      options: Options(
        contentType: 'multipart/form-data',
        sendTimeout: const Duration(seconds: 60),
        receiveTimeout: const Duration(seconds: 60),
      ),
    );

    return CropImageEntity.fromJson(
      response.data['data'] as Map<String, dynamic>,
    );
  }

  Future<CropStageEntity> markStageComplete({
    required String farmId,
    required String stageId,
  }) async {
    final response = await _dio.post(
      '/crops/$farmId/stages/$stageId/complete',
    );
    return CropStageEntity.fromJson(
      response.data['data'] as Map<String, dynamic>,
    );
  }
}
