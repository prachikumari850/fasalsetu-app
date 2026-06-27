import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/profile/data/datasources/profile_remote_datasource.dart';
import 'package:fasalsetu/features/auth/domain/entities/auth_entities.dart';

final profileRemoteDataSourceProvider = Provider<ProfileRemoteDataSource>(
  (ref) => ProfileRemoteDataSource(ref.watch(dioProvider)),
);

class ProfileNotifier extends AsyncNotifier<AuthUser> {
  @override
  Future<AuthUser> build() async {
    return ref.read(profileRemoteDataSourceProvider).getMe();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(profileRemoteDataSourceProvider).getMe(),
    );
  }

  Future<bool> updateMe(Map<String, dynamic> patch) async {
    try {
      final updated =
          await ref.read(profileRemoteDataSourceProvider).updateMe(patch);
      state = AsyncData(updated);
      return true;
    } catch (_) {
      return false;
    }
  }
}

final profileProvider = AsyncNotifierProvider<ProfileNotifier, AuthUser>(
  ProfileNotifier.new,
);