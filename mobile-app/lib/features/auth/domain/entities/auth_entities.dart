class AuthUser {
  final String id;
  final String email;
  final String fullName;
  final String? phone;
  final String role;
  final String? district;
  final String state;
  final bool isActive;
  final String preferredLang;

  const AuthUser({
    required this.id,
    required this.email,
    required this.fullName,
    this.phone,
    required this.role,
    this.district,
    required this.state,
    required this.isActive,
    required this.preferredLang,
  });

  factory AuthUser.fromJson(Map<String, dynamic> json) => AuthUser(
        id: json['id'] as String,
        email: json['email'] as String,
        fullName: json['full_name'] as String,
        phone: json['phone'] as String?,
        role: json['role'] as String,
        district: json['district'] as String?,
        state: json['state'] as String? ?? 'Uttar Pradesh',
        isActive: json['is_active'] as bool? ?? true,
        preferredLang: json['preferred_lang'] as String? ?? 'hi',
      );

  bool get isFarmer => role == 'farmer';
}

class AuthTokens {
  final String accessToken;
  final String refreshToken;
  final int expiresIn;
  final AuthUser user;

  const AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
    required this.user,
  });

  factory AuthTokens.fromJson(Map<String, dynamic> json) => AuthTokens(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
        expiresIn: json['expires_in'] as int? ?? 3600,
        user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
      );
}
