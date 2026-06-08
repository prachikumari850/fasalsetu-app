class AppConstants {
  AppConstants._();

  // API
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  // Supabase
  static const String supabaseUrl = String.fromEnvironment('SUPABASE_URL');
  static const String supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
  );

  // Storage keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userIdKey = 'user_id';
  static const String userRoleKey = 'user_role';
  static const String languageKey = 'preferred_lang';

  // Pagination
  static const int defaultPageSize = 20;

  // Image
  static const int maxImageSizeBytes = 10 * 1024 * 1024; // 10 MB
  static const double imageQuality = 85;

  // OTP
  static const int otpResendSeconds = 60;
  static const int otpLength = 6;

  // Map
  static const double defaultMapZoom = 15.0;
  static const double indiaLat = 20.5937;
  static const double indiaLng = 78.9629;

  // Trust score grades
  static const double gradeAMin = 80;
  static const double gradeBMin = 60;
  static const double gradeCMin = 40;
  static const double gradeDMin = 20;
}
