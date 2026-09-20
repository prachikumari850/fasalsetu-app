import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/crop/data/datasources/crop_remote_datasource.dart';
import 'package:fasalsetu/features/crop/domain/entities/crop_entities.dart';

final cropRemoteDataSourceProvider = Provider<CropRemoteDataSource>(
  (ref) => CropRemoteDataSource(ref.watch(dioProvider)),
);

final farmImagesProvider = FutureProvider.autoDispose
    .family<List<CropImageEntity>, String>(
  (ref, farmId) => ref.watch(cropRemoteDataSourceProvider).getFarmImages(farmId),
);

// Timeline provider — keyed by farm ID
class CropTimelineNotifier
    extends FamilyAsyncNotifier<CropTimelineEntity, String> {
  @override
  Future<CropTimelineEntity> build(String farmId) async {
    return ref.read(cropRemoteDataSourceProvider).getTimeline(farmId);
  }

  Future<void> refresh(String farmId) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(cropRemoteDataSourceProvider).getTimeline(farmId),
    );
  }

  Future<String?> uploadImage({
    required String farmId,
    required CropStageName stageName,
    required List<int> imageBytes,
    required String fileName,
    String? mimeType,
    required double latitude,
    required double longitude,
  }) async {
    try {
      await ref.read(cropRemoteDataSourceProvider).uploadImage(
            farmId: farmId,
            stageName: stageName,
            imageBytes: imageBytes,
            fileName: fileName,
            mimeType: mimeType,
            latitude: latitude,
            longitude: longitude,
            capturedAt: DateTime.now().toUtc(),
          );
      // Refresh timeline after upload
      await refresh(farmId);
      return null;
    } catch (e) {
      return _imageUploadErrorMessage(e);
    }
  }

  String _imageUploadErrorMessage(Object error) {
    if (error is! DioException) {
      return 'Unable to process the selected image. Please try another image.';
    }
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return 'The upload timed out. Please try again.';
    }
    if (error.type == DioExceptionType.connectionError) {
      return 'Unable to connect to the server. Please check your connection.';
    }
    switch (error.response?.statusCode) {
      case 400:
        return 'Invalid image request.';
      case 401:
      case 403:
        return 'Authentication failed. Please log in again.';
      case 404:
        return 'The selected farm or upload service was not found.';
      case 413:
        return 'Image is too large. Please select an image smaller than 10 MB.';
      case 422:
        return 'Invalid image or request data. Please choose a valid JPEG, PNG, or WebP image.';
      case 500:
        return 'Server error while processing the image. Please try again.';
      case 503:
        return 'The data service is temporarily unavailable. Please try again.';
      default:
        return 'Upload failed. Please try again.';
    }
  }

  Future<bool> markComplete({
    required String farmId,
    required String stageId,
  }) async {
    try {
      await ref.read(cropRemoteDataSourceProvider).markStageComplete(
            farmId: farmId,
            stageId: stageId,
          );
      await refresh(farmId);
      return true;
    } catch (e) {
      return false;
    }
  }
}

final cropTimelineProvider = AsyncNotifierProviderFamily<CropTimelineNotifier,
    CropTimelineEntity, String>(
  CropTimelineNotifier.new,
);
// Upload state (per farm+stage)
final imageUploadLoadingProvider = StateProvider<bool>((ref) => false);
