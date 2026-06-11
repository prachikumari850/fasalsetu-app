import 'package:fasalsetu/core/providers/auth_provider.dart';
import 'package:fasalsetu/core/providers/language_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/network/dio_client.dart';
import 'package:fasalsetu/features/auth/data/datasources/auth_remote_datasource.dart';

final authRemoteDataSourceProvider = Provider<AuthRemoteDataSource>((ref) {
  return AuthRemoteDataSource(ref.watch(dioProvider));
});

// OTP send state
class OtpSendNotifier extends AsyncNotifier<void> {
  @override
  Future<void> build() async {}

  Future<void> sendOtp({
    required String email,
    String preferredLang = 'hi',
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await ref.read(authRemoteDataSourceProvider).sendOtp(
            email: email,
            preferredLang: preferredLang,
          );
    });
  }
}

final otpSendProvider =
    AsyncNotifierProvider<OtpSendNotifier, void>(OtpSendNotifier.new);

// OTP verify state
class OtpVerifyNotifier extends AsyncNotifier<void> {
  @override
  Future<void> build() async {}

  Future<void> verifyOtp({
    required String email,
    required String otp,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final tokens = await ref
          .read(authRemoteDataSourceProvider)
          .verifyOtp(email: email, otp: otp);
      await ref.read(authProvider.notifier).setAuthenticated(tokens);

      // Update language based on user preference
      await ref
          .read(languageProvider.notifier)
          .setLocale(tokens.user.preferredLang);
    });
  }
}

final otpVerifyProvider =
    AsyncNotifierProvider<OtpVerifyNotifier, void>(OtpVerifyNotifier.new);
