import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:fasalsetu/core/constants/app_constants.dart';

class LanguageNotifier extends Notifier<Locale> {
  static const _storage = FlutterSecureStorage();

  @override
  Locale build() {
    _loadSavedLocale();
    return const Locale('hi');
  }

  Future<void> _loadSavedLocale() async {
    final lang = await _storage.read(key: AppConstants.languageKey);
    if (lang != null) {
      state = Locale(lang);
    }
  }

  Future<void> setLocale(String languageCode) async {
    await _storage.write(
      key: AppConstants.languageKey,
      value: languageCode,
    );
    state = Locale(languageCode);
  }

  bool get isHindi => state.languageCode == 'hi';
  bool get isEnglish => state.languageCode == 'en';
}

final languageProvider = NotifierProvider<LanguageNotifier, Locale>(
  LanguageNotifier.new,
);
