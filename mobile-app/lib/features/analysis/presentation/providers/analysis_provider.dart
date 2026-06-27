import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/analysis/data/datasources/analysis_remote_datasource.dart';
import 'package:fasalsetu/features/analysis/domain/entities/analysis_entities.dart';

final analysisRemoteDataSourceProvider = Provider<AnalysisRemoteDataSource>(
  (ref) => AnalysisRemoteDataSource(ref.watch(dioProvider)),
);

class AnalysisParams {
  final String farmId;
  final String imageId;
  const AnalysisParams({required this.farmId, required this.imageId});

  @override
  bool operator ==(Object other) =>
      other is AnalysisParams &&
      other.farmId == farmId &&
      other.imageId == imageId;

  @override
  int get hashCode => Object.hash(farmId, imageId);
}

final imageAnalysisProvider =
    FutureProvider.autoDispose.family<ImageAnalysisEntity, AnalysisParams>(
  (ref, params) => ref.watch(analysisRemoteDataSourceProvider).getImageAnalysis(
        farmId: params.farmId,
        imageId: params.imageId,
      ),
);