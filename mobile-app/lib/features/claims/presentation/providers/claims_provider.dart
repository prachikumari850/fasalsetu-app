// import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:fasalsetu/core/network/dio_client.dart';
// import 'package:fasalsetu/features/claims/data/datasources/claims_remote_datasource.dart';
// import 'package:fasalsetu/features/claims/domain/entities/claim_entities.dart';

// final claimsRemoteDataSourceProvider = Provider<ClaimsRemoteDataSource>(
//   (ref) => ClaimsRemoteDataSource(ref.watch(dioProvider)),
// );

// final claimsListProvider = FutureProvider.autoDispose<List<ClaimSummary>>(
//   (ref) => ref.watch(claimsRemoteDataSourceProvider).listClaims(),
// );

// final claimDetailProvider = FutureProvider.autoDispose.family<ClaimDetail, String>(
//   (ref, claimId) => ref.watch(claimsRemoteDataSourceProvider).getClaim(claimId),
// );

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/claims/data/datasources/claims_remote_datasource.dart';
import 'package:fasalsetu/features/claims/domain/entities/claim_entities.dart';

final claimsRemoteDataSourceProvider = Provider<ClaimsRemoteDataSource>(
  (ref) => ClaimsRemoteDataSource(ref.watch(dioProvider)),
);

class ClaimsListNotifier extends AsyncNotifier<List<ClaimSummary>> {
  @override
  Future<List<ClaimSummary>> build() async {
    return ref.read(claimsRemoteDataSourceProvider).listClaims();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(claimsRemoteDataSourceProvider).listClaims(),
    );
  }
}

final claimsListProvider =
    AsyncNotifierProvider<ClaimsListNotifier, List<ClaimSummary>>(
  ClaimsListNotifier.new,
);

final claimDetailProvider =
    FutureProvider.autoDispose.family<ClaimDetail, String>(
  (ref, claimId) => ref.read(claimsRemoteDataSourceProvider).getClaim(claimId),
);

class CreateClaimNotifier extends AsyncNotifier<ClaimSummary?> {
  @override
  Future<ClaimSummary?> build() async => null;

  Future<ClaimSummary?> submit(ClaimCreateRequest request) async {
    state = const AsyncLoading();
    ClaimSummary? created;
    state = await AsyncValue.guard(() async {
      created =
          await ref.read(claimsRemoteDataSourceProvider).createClaim(request);
      return created;
    });
    if (created != null) {
      await ref.read(claimsListProvider.notifier).refresh();
    }
    return created;
  }
}

final createClaimProvider =
    AsyncNotifierProvider<CreateClaimNotifier, ClaimSummary?>(
  CreateClaimNotifier.new,
);