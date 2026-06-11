// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'FasalSetu';

  @override
  String get tagline => 'Smart Farming, Secure Future';

  @override
  String get continueText => 'Continue';

  @override
  String get cancel => 'Cancel';

  @override
  String get save => 'Save';

  @override
  String get submit => 'Submit';

  @override
  String get back => 'Back';

  @override
  String get next => 'Next';

  @override
  String get retry => 'Retry';

  @override
  String get loading => 'Loading...';

  @override
  String get noData => 'No data available';

  @override
  String get error => 'Something went wrong';

  @override
  String get success => 'Success';

  @override
  String get networkError => 'No internet connection';

  @override
  String get serverError => 'Server error. Please try again.';

  @override
  String get loginTitle => 'Welcome to FasalSetu';

  @override
  String get loginSubtitle => 'Sign in to manage your farm';

  @override
  String get enterEmail => 'Enter your email address';

  @override
  String get emailLabel => 'Email Address';

  @override
  String get emailHint => 'farmer@example.com';

  @override
  String get emailRequired => 'Email is required';

  @override
  String get emailInvalid => 'Enter a valid email address';

  @override
  String get sendOtp => 'Send OTP';

  @override
  String get otpTitle => 'Verify OTP';

  @override
  String get otpSubtitle => 'Enter the 6-digit code sent to';

  @override
  String get otpLabel => 'Enter OTP';

  @override
  String get otpHint => '6-digit code';

  @override
  String get otpRequired => 'OTP is required';

  @override
  String get otpInvalid => 'OTP must be 6 digits';

  @override
  String get otpResend => 'Resend OTP';

  @override
  String otpResendIn(int seconds) {
    return 'Resend in ${seconds}s';
  }

  @override
  String get verifyOtp => 'Verify OTP';

  @override
  String get loginSuccess => 'Logged in successfully';

  @override
  String get logout => 'Logout';

  @override
  String get logoutConfirm => 'Are you sure you want to logout?';

  @override
  String get dashboardTitle => 'My Dashboard';

  @override
  String welcomeFarmer(String name) {
    return 'Hello, $name';
  }

  @override
  String get myFarms => 'My Farms';

  @override
  String get addFarm => 'Add Farm';

  @override
  String get noFarms => 'No farms registered yet';

  @override
  String get registerFarm => 'Register Your Farm';

  @override
  String get farmName => 'Farm Name';

  @override
  String get farmNameHint => 'e.g. Main Wheat Farm';

  @override
  String get farmNameRequired => 'Farm name is required';

  @override
  String get village => 'Village';

  @override
  String get villageHint => 'Enter village name';

  @override
  String get villageRequired => 'Village is required';

  @override
  String get district => 'District';

  @override
  String get districtHint => 'Enter district';

  @override
  String get districtRequired => 'District is required';

  @override
  String get state => 'State';

  @override
  String get areaAcres => 'Area (in acres)';

  @override
  String get areaHint => 'e.g. 2.5';

  @override
  String get areaRequired => 'Area is required';

  @override
  String get cropType => 'Crop Type';

  @override
  String get cropTypeHint => 'e.g. Wheat, Rice, Cotton';

  @override
  String get cropTypeRequired => 'Crop type is required';

  @override
  String get season => 'Season';

  @override
  String get seasonHint => 'e.g. Rabi 2024-25';

  @override
  String get seasonRequired => 'Season is required';

  @override
  String get khasraNumber => 'Khasra Number (optional)';

  @override
  String get drawBoundary => 'Draw Farm Boundary';

  @override
  String get boundaryRequired => 'Please draw the farm boundary';

  @override
  String boundaryPoints(int count) {
    return '$count boundary points marked';
  }

  @override
  String get farmRegistered => 'Farm registered successfully';

  @override
  String get farmDetails => 'Farm Details';

  @override
  String get cropLifecycle => 'Crop Lifecycle';

  @override
  String get sowing => 'Sowing';

  @override
  String get germination => 'Germination';

  @override
  String get vegetative => 'Vegetative Stage';

  @override
  String get flowering => 'Flowering';

  @override
  String get preHarvest => 'Pre-Harvest';

  @override
  String get uploadPhoto => 'Upload Photo';

  @override
  String get takePhoto => 'Take Photo';

  @override
  String get chooseFromGallery => 'Choose from Gallery';

  @override
  String get photoUploaded => 'Photo uploaded successfully';

  @override
  String get gpsRequired => 'GPS location is required for photos';

  @override
  String get stageCompleted => 'Stage marked as complete';

  @override
  String get advisories => 'Advisories';

  @override
  String get noAdvisories => 'No advisories at this time';

  @override
  String get markAsRead => 'Mark as Read';

  @override
  String get priority => 'Priority';

  @override
  String get urgent => 'Urgent';

  @override
  String get high => 'High';

  @override
  String get medium => 'Medium';

  @override
  String get low => 'Low';

  @override
  String get claims => 'Claims';

  @override
  String get myClaims => 'My Claims';

  @override
  String get newClaim => 'New Claim';

  @override
  String get noClaims => 'No claims submitted yet';

  @override
  String get claimStatus => 'Claim Status';

  @override
  String get submitted => 'Submitted';

  @override
  String get underReview => 'Under Review';

  @override
  String get approved => 'Approved';

  @override
  String get rejected => 'Rejected';

  @override
  String get needsInspection => 'Needs Inspection';

  @override
  String get damageType => 'Damage Type';

  @override
  String get drought => 'Drought';

  @override
  String get flood => 'Flood';

  @override
  String get hail => 'Hail';

  @override
  String get pest => 'Pest Attack';

  @override
  String get disease => 'Disease';

  @override
  String get fire => 'Fire';

  @override
  String get other => 'Other';

  @override
  String get damageDescription => 'Describe the damage';

  @override
  String get estimatedLoss => 'Estimated Loss (₹)';

  @override
  String get affectedAcres => 'Affected Area (acres)';

  @override
  String get claimSubmitted => 'Claim submitted successfully';

  @override
  String get claimDetails => 'Claim Details';

  @override
  String get trustScore => 'Trust Score';

  @override
  String get profile => 'Profile';

  @override
  String get myProfile => 'My Profile';

  @override
  String get fullName => 'Full Name';

  @override
  String get phone => 'Phone Number';

  @override
  String get language => 'Language';

  @override
  String get english => 'English';

  @override
  String get hindi => 'Hindi';

  @override
  String get settings => 'Settings';

  @override
  String get notifications => 'Notifications';

  @override
  String get noNotifications => 'No notifications';

  @override
  String get allNotifications => 'All Notifications';

  @override
  String get healthScore => 'Health Score';

  @override
  String get diseaseDetected => 'Disease Detected';

  @override
  String get pestDetected => 'Pest Detected';

  @override
  String get healthy => 'Healthy';

  @override
  String get cropHealth => 'Crop Health';

  @override
  String get aiAnalysis => 'AI Analysis';

  @override
  String get confidence => 'Confidence';
}
