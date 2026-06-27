import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/health/data/datasources/health_remote_datasource.dart';
import 'package:fasalsetu/features/health/domain/entities/health_entities.dart';

final healthRemoteDataSourceProvider = Provider<HealthRemoteDataSource>(
  (ref) => HealthRemoteDataSource(ref.watch(dioProvider)),
);

final cropHealthProvider =
    FutureProvider.autoDispose.family<CropHealthEntity, String>(
  (ref, farmId) =>
      ref.watch(healthRemoteDataSourceProvider).getFarmHealth(farmId),
);