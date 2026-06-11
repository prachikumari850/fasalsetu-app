import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/farm/data/datasources/farm_remote_datasource.dart';
import 'package:fasalsetu/features/farm/domain/entities/farm_entity.dart';

final farmRemoteDataSourceProvider = Provider<FarmRemoteDataSource>(
  (ref) => FarmRemoteDataSource(ref.watch(dioProvider)),
);

// My farms list
class MyFarmsNotifier extends AsyncNotifier<List<FarmEntity>> {
  @override
  Future<List<FarmEntity>> build() async {
    return ref.read(farmRemoteDataSourceProvider).getMyFarms();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(farmRemoteDataSourceProvider).getMyFarms(),
    );
  }

  void addFarm(FarmEntity farm) {
    state.whenData(
      (farms) => state = AsyncData([farm, ...farms]),
    );
  }

  Future<void> removeFarm(String farmId) async {
    await ref.read(farmRemoteDataSourceProvider).deleteFarm(farmId);
    state.whenData(
      (farms) => state = AsyncData(
        farms.where((f) => f.id != farmId).toList(),
      ),
    );
  }
}

final myFarmsProvider =
    AsyncNotifierProvider<MyFarmsNotifier, List<FarmEntity>>(
  MyFarmsNotifier.new,
);

// Create farm state
class CreateFarmNotifier extends AsyncNotifier<FarmEntity?> {
  @override
  Future<FarmEntity?> build() async => null;

  Future<FarmEntity?> createFarm(Map<String, dynamic> data) async {
    state = const AsyncLoading();
    FarmEntity? created;
    state = await AsyncValue.guard(() async {
      created = await ref.read(farmRemoteDataSourceProvider).createFarm(data);
      return created;
    });
    if (created != null) {
      ref.read(myFarmsProvider.notifier).addFarm(created!);
    }
    return created;
  }
}

final createFarmProvider =
    AsyncNotifierProvider<CreateFarmNotifier, FarmEntity?>(
  CreateFarmNotifier.new,
);
