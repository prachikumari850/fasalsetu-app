import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:fasalsetu/core/constants/app_constants.dart';
import 'package:fasalsetu/core/providers/auth_provider.dart';

const _storage = FlutterSecureStorage();

Dio createDio(Ref ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: AppConstants.apiBaseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
    ),
  );

  // Auth interceptor
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final authState = ref.read(authProvider);
        final token = authState.accessToken ??
            await _storage.read(key: AppConstants.accessTokenKey);

        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          // Do not immediately clear the session for every 401.
          // Some protected endpoints can temporarily return 401 while the
          // user is still authenticated, and forcing logout causes the app
          // to loop back to login.
          // The request error is still surfaced to the caller.
        }
        handler.next(error);
      },
    ),
  );

  return dio;
}

final dioProvider = Provider<Dio>((ref) => createDio(ref));
