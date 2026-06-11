import 'package:dio/dio.dart';
import 'package:fasalsetu/features/auth/domain/entities/auth_entities.dart';

class AuthRemoteDataSource {
  final Dio _dio;
  AuthRemoteDataSource(this._dio);

  Future<void> sendOtp({
    required String email,
    String? fullName,
    String preferredLang = 'hi',
  }) async {
    await _dio.post(
      '/auth/otp/send',
      data: {
        'email': email,
        if (fullName != null) 'full_name': fullName,
        'preferred_lang': preferredLang,
      },
    );
  }

  Future<AuthTokens> verifyOtp({
    required String email,
    required String otp,
  }) async {
    final response = await _dio.post(
      '/auth/otp/verify',
      data: {'email': email, 'otp': otp},
    );
    return AuthTokens.fromJson(
      response.data['data'] as Map<String, dynamic>,
    );
  }
}
