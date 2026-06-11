import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  // Brand
  static const Color primary = Color(0xFF2E7D32); // Forest green
  static const Color primaryLight = Color(0xFF60AD5E);
  static const Color primaryDark = Color(0xFF005005);
  static const Color secondary = Color(0xFFF9A825); // Harvest gold
  static const Color secondaryLight = Color(0xFFFFD95A);
  static const Color secondaryDark = Color(0xFFC17900);

  // Semantic
  static const Color success = Color(0xFF388E3C);
  static const Color warning = Color(0xFFF57C00);
  static const Color error = Color(0xFFC62828);
  static const Color info = Color(0xFF1565C0);

  // Neutrals
  static const Color background = Color(0xFFF5F5F0);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF0F4F0);
  static const Color border = Color(0xFFE0E4E0);
  static const Color textPrimary = Color(0xFF1A1C1A);
  static const Color textSecondary = Color(0xFF4A4D4A);
  static const Color textHint = Color(0xFF9E9E9E);
  static const Color divider = Color(0xFFEEEEEE);

  // Claim status colors
  static const Color statusDraft = Color(0xFF9E9E9E);
  static const Color statusSubmitted = Color(0xFF1565C0);
  static const Color statusUnderReview = Color(0xFFF57C00);
  static const Color statusApproved = Color(0xFF388E3C);
  static const Color statusRejected = Color(0xFFC62828);
  static const Color statusInspection = Color(0xFF6A1B9A);

  // Advisory priority colors
  static const Color priorityUrgent = Color(0xFFC62828);
  static const Color priorityHigh = Color(0xFFF57C00);
  static const Color priorityMedium = Color(0xFF1565C0);
  static const Color priorityLow = Color(0xFF388E3C);

  // Trust score grade colors
  static const Color gradeA = Color(0xFF1B5E20);
  static const Color gradeB = Color(0xFF388E3C);
  static const Color gradeC = Color(0xFFF57C00);
  static const Color gradeD = Color(0xFFE64A19);
  static const Color gradeF = Color(0xFFC62828);
}
