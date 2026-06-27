// import 'package:dio/dio.dart';
// import 'package:fasalsetu/features/claims/domain/entities/claim_entities.dart';

// class ClaimsRemoteDataSource {
//   final Dio _dio;
//   ClaimsRemoteDataSource(this._dio);

//   Future<List<ClaimSummary>> listClaims() async {
//     final response = await _dio.get('/claims');
//     final data = response.data['data'] as List;
//     return data.map((j) => ClaimSummary.fromJson(j as Map<String, dynamic>)).toList();
//   }

//   Future<ClaimDetail> getClaim(String claimId) async {
//     final response = await _dio.get('/claims/$claimId');
//     return ClaimDetail.fromJson(response.data['data'] as Map<String, dynamic>);
//   }
// }

import 'package:dio/dio.dart';
import 'package:fasalsetu/features/claims/domain/entities/claim_entities.dart';

class ClaimsRemoteDataSource {
  final Dio _dio;
  ClaimsRemoteDataSource(this._dio);

  Future<List<ClaimSummary>> listClaims() async {
    final response = await _dio.get('/claims');
    final data = response.data['data'] as List;
    return data
        .map((j) => ClaimSummary.fromJson(j as Map<String, dynamic>))
        .toList();
  }

  Future<ClaimDetail> getClaim(String claimId) async {
    final response = await _dio.get('/claims/$claimId');
    return ClaimDetail.fromJson(response.data['data'] as Map<String, dynamic>);
  }

  Future<ClaimSummary> createClaim(ClaimCreateRequest request) async {
    final response = await _dio.post('/claims', data: request.toJson());
    return ClaimSummary.fromJson(response.data['data'] as Map<String, dynamic>);
  }
}