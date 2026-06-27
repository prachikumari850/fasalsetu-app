import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/advisory/data/datasources/advisory_remote_datasource.dart';
import 'package:fasalsetu/features/advisory/domain/entities/advisory_entities.dart';

final advisoryRemoteDataSourceProvider = Provider<AdvisoryRemoteDataSource>(
  (ref) => AdvisoryRemoteDataSource(ref.watch(dioProvider)),
);

final advisoriesProvider =
    FutureProvider.autoDispose.family<List<AdvisoryEntity>, String>(
  (ref, farmId) =>
      ref.watch(advisoryRemoteDataSourceProvider).getAdvisories(farmId),
);