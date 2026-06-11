import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/crop/data/datasources/crop_remote_datasource.dart';
import 'package:fasalsetu/features/crop/domain/entities/crop_entities.dart';

final cropRemoteDataSourceProvider = Provider<CropRemoteDataSource>(
  (ref) => CropRemoteDataSource(ref.watch(dioProvider)),
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

  Future<bool> uploadImage({
    required String farmId,
    required CropStageName stageName,
    required File imageFile,
    required double latitude,
    required double longitude,
  }) async {
    try {
      await ref.read(cropRemoteDataSourceProvider).uploadImage(
            farmId: farmId,
            stageName: stageName,
            imageFile: imageFile,
            latitude: latitude,
            longitude: longitude,
            capturedAt: DateTime.now().toUtc(),
          );
      // Refresh timeline after upload
      await refresh(farmId);
      return true;
    } catch (e) {
      return false;
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
