import 'package:dio/dio.dart';
import 'package:fasalsetu/features/auth/domain/entities/auth_entities.dart';

class ProfileRemoteDataSource {
  final Dio _dio;
  ProfileRemoteDataSource(this._dio);

  Future<AuthUser> getMe() async {
    final response = await _dio.get('/auth/me');
    return AuthUser.fromJson(response.data['data'] as Map<String, dynamic>);
  }

  Future<AuthUser> updateMe(Map<String, dynamic> patch) async {
    final response = await _dio.put('/auth/me', data: patch);
    return AuthUser.fromJson(response.data['data'] as Map<String, dynamic>);
  }
}