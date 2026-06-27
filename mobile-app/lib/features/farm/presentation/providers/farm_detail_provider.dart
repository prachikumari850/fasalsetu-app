import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/features/farm/presentation/providers/farm_provider.dart';
import 'package:fasalsetu/features/farm/domain/entities/farm_entity.dart';

/// Single-farm detail fetch. Reuses the existing
/// farmRemoteDataSourceProvider already defined in farm_provider.dart —
/// no new datasource, no duplicate class.
final farmDetailProvider =
    FutureProvider.autoDispose.family<FarmEntity, String>(
  (ref, farmId) =>
      ref.read(farmRemoteDataSourceProvider).getFarm(farmId),
);