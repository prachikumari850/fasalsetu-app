import 'package:dio/dio.dart';
import 'package:fasalsetu/features/farm/domain/entities/farm_entity.dart';

class FarmRemoteDataSource {
  final Dio _dio;
  FarmRemoteDataSource(this._dio);

  Future<List<FarmEntity>> getMyFarms() async {
    final response = await _dio.get('/farms/my');
    final data = response.data['data'] as List<dynamic>;
    return data
        .map((e) => FarmEntity.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<FarmEntity> getFarm(String farmId) async {
    final response = await _dio.get('/farms/$farmId');
    return FarmEntity.fromJson(
      response.data['data'] as Map<String, dynamic>,
    );
  }

  Future<FarmEntity> createFarm(Map<String, dynamic> data) async {
    final response = await _dio.post('/farms', data: data);
    return FarmEntity.fromJson(
      response.data['data'] as Map<String, dynamic>,
    );
  }

  Future<void> deleteFarm(String farmId) async {
    await _dio.delete('/farms/$farmId');
  }
}
