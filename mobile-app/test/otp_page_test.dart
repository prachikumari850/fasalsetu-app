import 'package:fasalsetu/features/auth/presentation/pages/otp_page.dart';
import 'package:fasalsetu/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

Widget buildOtpPage() {
  return ProviderScope(
    child: MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: const OtpPage(email: 'farmer@example.com'),
    ),
  );
}

void main() {
  testWidgets('shows six responsive OTP boxes and disables verify when incomplete',
      (tester) async {
    await tester.binding.setSurfaceSize(const Size(280, 800));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(buildOtpPage());
    await tester.pump();

    expect(find.byType(TextFormField), findsNWidgets(6));
    expect(tester.takeException(), isNull);
    expect(
      tester.widget<ElevatedButton>(
        find.widgetWithText(ElevatedButton, 'Verify OTP'),
      ).onPressed,
      isNull,
    );
  });

  testWidgets('distributes a pasted six-digit OTP and enables verify',
      (tester) async {
    await tester.pumpWidget(buildOtpPage());
    await tester.pump();

    await tester.enterText(find.byType(TextFormField).first, '012345');
    await tester.pump();

    final fields = tester.widgetList<TextFormField>(find.byType(TextFormField));
    expect(fields.map((field) => field.controller!.text),
        equals(['0', '1', '2', '3', '4', '5']));
    expect(
      tester.widget<ElevatedButton>(
        find.widgetWithText(ElevatedButton, 'Verify OTP'),
      ).onPressed,
      isNotNull,
    );
  });
}
