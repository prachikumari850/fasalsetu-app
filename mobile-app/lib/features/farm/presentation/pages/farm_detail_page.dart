import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class FarmDetailPage extends StatelessWidget {
  final String farmId;
  const FarmDetailPage({super.key, required this.farmId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Farm Detail'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => context.pop(),
        ),
      ),
      body: Center(child: Text('Farm: $farmId — Phase 10')),
    );
  }
}
