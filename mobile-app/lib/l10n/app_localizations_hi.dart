// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Hindi (`hi`).
class AppLocalizationsHi extends AppLocalizations {
  AppLocalizationsHi([String locale = 'hi']) : super(locale);

  @override
  String get appName => 'फसलसेतु';

  @override
  String get tagline => 'स्मार्ट खेती, सुरक्षित भविष्य';

  @override
  String get continueText => 'जारी रखें';

  @override
  String get cancel => 'रद्द करें';

  @override
  String get save => 'सहेजें';

  @override
  String get submit => 'जमा करें';

  @override
  String get back => 'वापस';

  @override
  String get next => 'अगला';

  @override
  String get retry => 'पुनः प्रयास';

  @override
  String get loading => 'लोड हो रहा है...';

  @override
  String get noData => 'कोई डेटा उपलब्ध नहीं';

  @override
  String get error => 'कुछ गलत हुआ';

  @override
  String get success => 'सफल';

  @override
  String get networkError => 'इंटरनेट कनेक्शन नहीं है';

  @override
  String get serverError => 'सर्वर त्रुटि। कृपया पुनः प्रयास करें।';

  @override
  String get loginTitle => 'फसलसेतु में आपका स्वागत है';

  @override
  String get loginSubtitle => 'अपने खेत का प्रबंधन करने के लिए लॉगिन करें';

  @override
  String get enterEmail => 'अपना ईमेल पता दर्ज करें';

  @override
  String get emailLabel => 'ईमेल पता';

  @override
  String get emailHint => 'kisan@example.com';

  @override
  String get emailRequired => 'ईमेल आवश्यक है';

  @override
  String get emailInvalid => 'मान्य ईमेल दर्ज करें';

  @override
  String get sendOtp => 'OTP भेजें';

  @override
  String get otpTitle => 'OTP सत्यापित करें';

  @override
  String get otpSubtitle => 'इस पर भेजा गया 6-अंकीय कोड दर्ज करें';

  @override
  String get otpLabel => 'OTP दर्ज करें';

  @override
  String get otpHint => '6-अंकीय कोड';

  @override
  String get otpRequired => 'OTP आवश्यक है';

  @override
  String get otpInvalid => 'OTP 6 अंकों का होना चाहिए';

  @override
  String get otpResend => 'OTP दोबारा भेजें';

  @override
  String otpResendIn(int seconds) {
    return '$seconds सेकंड में दोबारा भेजें';
  }

  @override
  String get verifyOtp => 'OTP सत्यापित करें';

  @override
  String get loginSuccess => 'सफलतापूर्वक लॉगिन हुए';

  @override
  String get logout => 'लॉगआउट';

  @override
  String get logoutConfirm => 'क्या आप लॉगआउट करना चाहते हैं?';

  @override
  String get dashboardTitle => 'मेरा डैशबोर्ड';

  @override
  String welcomeFarmer(String name) {
    return 'नमस्ते, $name';
  }

  @override
  String get myFarms => 'मेरे खेत';

  @override
  String get addFarm => 'खेत जोड़ें';

  @override
  String get noFarms => 'अभी तक कोई खेत पंजीकृत नहीं है';

  @override
  String get registerFarm => 'अपना खेत पंजीकृत करें';

  @override
  String get farmName => 'खेत का नाम';

  @override
  String get farmNameHint => 'जैसे: मुख्य गेहूँ का खेत';

  @override
  String get farmNameRequired => 'खेत का नाम आवश्यक है';

  @override
  String get village => 'गाँव';

  @override
  String get villageHint => 'गाँव का नाम दर्ज करें';

  @override
  String get villageRequired => 'गाँव आवश्यक है';

  @override
  String get district => 'जिला';

  @override
  String get districtHint => 'जिला दर्ज करें';

  @override
  String get districtRequired => 'जिला आवश्यक है';

  @override
  String get state => 'राज्य';

  @override
  String get areaAcres => 'क्षेत्रफल (एकड़ में)';

  @override
  String get areaHint => 'जैसे: 2.5';

  @override
  String get areaRequired => 'क्षेत्रफल आवश्यक है';

  @override
  String get cropType => 'फसल का प्रकार';

  @override
  String get cropTypeHint => 'जैसे: गेहूँ, चावल, कपास';

  @override
  String get cropTypeRequired => 'फसल का प्रकार आवश्यक है';

  @override
  String get season => 'मौसम';

  @override
  String get seasonHint => 'जैसे: रबी 2024-25';

  @override
  String get seasonRequired => 'मौसम आवश्यक है';

  @override
  String get khasraNumber => 'खसरा नंबर (वैकल्पिक)';

  @override
  String get drawBoundary => 'खेत की सीमा बनाएं';

  @override
  String get boundaryRequired => 'कृपया खेत की सीमा बनाएं';

  @override
  String boundaryPoints(int count) {
    return '$count सीमा बिंदु अंकित';
  }

  @override
  String get farmRegistered => 'खेत सफलतापूर्वक पंजीकृत हुआ';

  @override
  String get farmDetails => 'खेत का विवरण';

  @override
  String get cropLifecycle => 'फसल जीवनचक्र';

  @override
  String get sowing => 'बुआई';

  @override
  String get germination => 'अंकुरण';

  @override
  String get vegetative => 'वानस्पतिक अवस्था';

  @override
  String get flowering => 'फूल आना';

  @override
  String get preHarvest => 'पूर्व-कटाई';

  @override
  String get uploadPhoto => 'फोटो अपलोड करें';

  @override
  String get takePhoto => 'फोटो लें';

  @override
  String get chooseFromGallery => 'गैलरी से चुनें';

  @override
  String get photoUploaded => 'फोटो सफलतापूर्वक अपलोड हुई';

  @override
  String get gpsRequired => 'फोटो के लिए GPS स्थान आवश्यक है';

  @override
  String get stageCompleted => 'चरण पूर्ण के रूप में चिह्नित';

  @override
  String get advisories => 'सलाहें';

  @override
  String get noAdvisories => 'अभी कोई सलाह नहीं';

  @override
  String get markAsRead => 'पढ़ा हुआ चिह्नित करें';

  @override
  String get priority => 'प्राथमिकता';

  @override
  String get urgent => 'अत्यावश्यक';

  @override
  String get high => 'उच्च';

  @override
  String get medium => 'मध्यम';

  @override
  String get low => 'कम';

  @override
  String get claims => 'दावे';

  @override
  String get myClaims => 'मेरे दावे';

  @override
  String get newClaim => 'नया दावा';

  @override
  String get noClaims => 'अभी तक कोई दावा नहीं';

  @override
  String get claimStatus => 'दावे की स्थिति';

  @override
  String get submitted => 'जमा किया';

  @override
  String get underReview => 'समीक्षाधीन';

  @override
  String get approved => 'स्वीकृत';

  @override
  String get rejected => 'अस्वीकृत';

  @override
  String get needsInspection => 'निरीक्षण आवश्यक';

  @override
  String get damageType => 'नुकसान का प्रकार';

  @override
  String get drought => 'सूखा';

  @override
  String get flood => 'बाढ़';

  @override
  String get hail => 'ओले';

  @override
  String get pest => 'कीट हमला';

  @override
  String get disease => 'बीमारी';

  @override
  String get fire => 'आग';

  @override
  String get other => 'अन्य';

  @override
  String get damageDescription => 'नुकसान का विवरण दें';

  @override
  String get estimatedLoss => 'अनुमानित नुकसान (₹)';

  @override
  String get affectedAcres => 'प्रभावित क्षेत्र (एकड़)';

  @override
  String get claimSubmitted => 'दावा सफलतापूर्वक जमा हुआ';

  @override
  String get claimDetails => 'दावे का विवरण';

  @override
  String get trustScore => 'विश्वास स्कोर';

  @override
  String get profile => 'प्रोफ़ाइल';

  @override
  String get myProfile => 'मेरी प्रोफ़ाइल';

  @override
  String get fullName => 'पूरा नाम';

  @override
  String get phone => 'फोन नंबर';

  @override
  String get language => 'भाषा';

  @override
  String get english => 'अंग्रेजी';

  @override
  String get hindi => 'हिंदी';

  @override
  String get settings => 'सेटिंग्स';

  @override
  String get notifications => 'सूचनाएं';

  @override
  String get noNotifications => 'कोई सूचना नहीं';

  @override
  String get allNotifications => 'सभी सूचनाएं';

  @override
  String get healthScore => 'स्वास्थ्य स्कोर';

  @override
  String get diseaseDetected => 'बीमारी मिली';

  @override
  String get pestDetected => 'कीट मिला';

  @override
  String get healthy => 'स्वस्थ';

  @override
  String get cropHealth => 'फसल स्वास्थ्य';

  @override
  String get aiAnalysis => 'AI विश्लेषण';

  @override
  String get confidence => 'विश्वसनीयता';
}
