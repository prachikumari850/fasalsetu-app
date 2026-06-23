import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fasalsetu/core/constants/app_constants.dart';
import 'package:fasalsetu/core/providers/auth_provider.dart';

Dio createDio(Ref ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: AppConstants.apiBaseUrl,
      // Increased from 15s to 60s.
      // Root cause of timeout: backend makes N SSL connections (one per farm)
      // Fix is in farms.py (batch fetch), but 60s is a safety net for slow
      // networks and any other endpoints that may still be slower.
      connectTimeout: const Duration(seconds: 60),
      receiveTimeout: const Duration(seconds: 60),
      sendTimeout:    const Duration(seconds: 60),
      headers: {'Content-Type': 'application/json'},
    ),
  );

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) {
        // Read token directly from Riverpod in-memory state.
        // Do NOT use FlutterSecureStorage here — localStorage on Flutter Web
        // is unreliable and can return null even when the user is authenticated.
        final token = ref.read(authProvider).accessToken;
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          // Token expired or invalid — sign out
          ref.read(authProvider.notifier).signOut();
        }
        handler.next(error);
      },
    ),
  );

  return dio;
}

final dioProvider = Provider<Dio>((ref) => createDio(ref));