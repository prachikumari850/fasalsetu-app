import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/trust/data/datasources/trust_remote_datasource.dart';
import 'package:fasalsetu/features/trust/domain/entities/trust_entities.dart';

final trustRemoteDataSourceProvider = Provider<TrustRemoteDataSource>(
  (ref) => TrustRemoteDataSource(ref.watch(dioProvider)),
);

final trustScoreProvider =
    FutureProvider.autoDispose.family<TrustScoreEntity, String>(
  (ref, farmId) =>
      ref.watch(trustRemoteDataSourceProvider).getTrustScore(farmId),
);