import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:fasalsetu/core/constants/app_constants.dart';
import 'package:fasalsetu/features/auth/domain/entities/auth_entities.dart';

enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthState {
  final AuthStatus status;
  final AuthUser? user;
  final String? accessToken;

  const AuthState({
    required this.status,
    this.user,
    this.accessToken,
  });

  const AuthState.unknown()
      : status = AuthStatus.unknown,
        user = null,
        accessToken = null;

  const AuthState.unauthenticated()
      : status = AuthStatus.unauthenticated,
        user = null,
        accessToken = null;

  AuthState.authenticated({
    required AuthUser user,
    required String accessToken,
  })  : status = AuthStatus.authenticated,
        user = user,
        accessToken = accessToken;

  bool get isAuthenticated => status == AuthStatus.authenticated;
}

class AuthNotifier extends Notifier<AuthState> {
  static const _storage = FlutterSecureStorage();

  @override
  AuthState build() {
    _initialize();
    return const AuthState.unknown();
  }

  Future<void> _initialize() async {
    try {
      final token = await _storage.read(key: AppConstants.accessTokenKey);
      final userId = await _storage.read(key: AppConstants.userIdKey);
      final role = await _storage.read(key: AppConstants.userRoleKey);
      final email = await _storage.read(key: 'user_email');
      final fullName = await _storage.read(key: 'user_full_name');
      final preferredLang = await _storage.read(key: AppConstants.languageKey);

      if (token != null && userId != null) {
        state = AuthState.authenticated(
          accessToken: token,
          user: AuthUser(
            id: userId,
            email: email ?? '',
            fullName: fullName ?? '',
            role: role ?? 'farmer',
            state: 'Uttar Pradesh',
            isActive: true,
            preferredLang: preferredLang ?? 'hi',
          ),
        );
      } else {
        state = const AuthState.unauthenticated();
      }
    } catch (_) {
      state = const AuthState.unauthenticated();
    }
  }

  Future<void> setAuthenticated(AuthTokens tokens) async {
    await _storage.write(
      key: AppConstants.accessTokenKey,
      value: tokens.accessToken,
    );
    await _storage.write(
      key: AppConstants.refreshTokenKey,
      value: tokens.refreshToken,
    );
    await _storage.write(
      key: AppConstants.userIdKey,
      value: tokens.user.id,
    );
    await _storage.write(
      key: AppConstants.userRoleKey,
      value: tokens.user.role,
    );
    await _storage.write(key: 'user_email', value: tokens.user.email);
    await _storage.write(key: 'user_full_name', value: tokens.user.fullName);
    await _storage.write(
      key: AppConstants.languageKey,
      value: tokens.user.preferredLang,
    );

    state = AuthState.authenticated(
      accessToken: tokens.accessToken,
      user: tokens.user,
    );
  }

  Future<void> signOut() async {
    await _storage.deleteAll();
    state = const AuthState.unauthenticated();
  }
}

final authProvider = NotifierProvider<AuthNotifier, AuthState>(
  AuthNotifier.new,
);
