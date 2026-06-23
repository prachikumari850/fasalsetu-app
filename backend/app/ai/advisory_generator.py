from __future__ import annotations
from app.models.crop import SeverityLevel, AdvisoryPriority
import structlog

logger = structlog.get_logger()

# Bilingual advisory database for each disease/condition
ADVISORY_DB: dict[str, dict] = {
    "healthy": {
        "title_en": "Crop is Healthy",
        "title_hi": "फसल स्वस्थ है",
        "body_en": (
            "Your crop shows no signs of disease or pest infestation. "
            "Continue regular monitoring and maintain proper irrigation. "
            "Apply balanced fertilizer as per schedule."
        ),
        "body_hi": (
            "आपकी फसल में बीमारी या कीट का कोई संकेत नहीं है। "
            "नियमित निगरानी जारी रखें और उचित सिंचाई बनाए रखें। "
            "निर्धारित समय पर संतुलित उर्वरक डालें।"
        ),
        "priority": AdvisoryPriority.low,
        "severity": SeverityLevel.low,
    },
    "leaf_blast": {
        "title_en": "Leaf Blast Detected",
        "title_hi": "पत्ती झुलसा रोग मिला",
        "body_en": (
            "Leaf blast (Magnaporthe oryzae) detected on your rice crop. "
            "Immediately apply Tricyclazole 75 WP at 0.6g/L water or "
            "Isoprothiolane 40 EC at 1.5mL/L. "
            "Avoid excess nitrogen fertilizer. Ensure proper field drainage. "
            "Spray early morning or evening for best results."
        ),
        "body_hi": (
            "आपकी धान की फसल में पत्ती झुलसा रोग (Magnaporthe oryzae) मिला है। "
            "तुरंत ट्राइसाइक्लाज़ोल 75 WP 0.6 ग्राम प्रति लीटर पानी में या "
            "आइसोप्रोथियोलेन 40 EC 1.5 मिली प्रति लीटर डालें। "
            "अधिक नाइट्रोजन उर्वरक से बचें। खेत में उचित जल निकासी सुनिश्चित करें। "
            "बेहतर परिणाम के लिए सुबह या शाम को स्प्रे करें।"
        ),
        "priority": AdvisoryPriority.urgent,
        "severity": SeverityLevel.high,
    },
    "brown_spot": {
        "title_en": "Brown Spot Disease Detected",
        "title_hi": "भूरा धब्बा रोग मिला",
        "body_en": (
            "Brown spot (Bipolaris oryzae) detected. "
            "Apply Mancozeb 75 WP at 2g/L or Propiconazole 25 EC at 1mL/L. "
            "Ensure adequate potassium fertilization. "
            "Treat seeds with Thiram before next sowing."
        ),
        "body_hi": (
            "भूरा धब्बा रोग (Bipolaris oryzae) मिला है। "
            "मैंकोज़ेब 75 WP 2 ग्राम प्रति लीटर या प्रोपिकोनाज़ोल 25 EC 1 मिली प्रति लीटर डालें। "
            "पर्याप्त पोटाश उर्वरक सुनिश्चित करें। "
            "अगली बुआई से पहले थीरम से बीज उपचार करें।"
        ),
        "priority": AdvisoryPriority.high,
        "severity": SeverityLevel.medium,
    },
    "bacterial_blight": {
        "title_en": "Bacterial Blight Detected",
        "title_hi": "जीवाणु अंगमारी रोग मिला",
        "body_en": (
            "Bacterial blight (Xanthomonas oryzae) detected. "
            "There is no effective cure — focus on preventing spread. "
            "Remove and burn infected plant material immediately. "
            "Apply Copper oxychloride 50 WP at 3g/L as protective spray. "
            "Avoid flood irrigation. Use resistant varieties in next season."
        ),
        "body_hi": (
            "जीवाणु अंगमारी (Xanthomonas oryzae) मिली है। "
            "इसका कोई प्रभावी इलाज नहीं है — प्रसार रोकने पर ध्यान दें। "
            "संक्रमित पौधों को तुरंत हटाएं और जलाएं। "
            "कॉपर ऑक्सीक्लोराइड 50 WP 3 ग्राम प्रति लीटर सुरक्षात्मक स्प्रे करें। "
            "बाढ़ सिंचाई से बचें। अगले मौसम में रोग प्रतिरोधी किस्में उगाएं।"
        ),
        "priority": AdvisoryPriority.urgent,
        "severity": SeverityLevel.critical,
    },
    "yellow_rust": {
        "title_en": "Yellow Rust Detected on Wheat",
        "title_hi": "गेहूँ में पीली रतुआ मिली",
        "body_en": (
            "Yellow rust (Puccinia striiformis) detected on wheat. "
            "Apply Propiconazole 25 EC at 1mL/L or Tebuconazole 25.9 EC at 1mL/L immediately. "
            "Spray at 7-10 day intervals if disease persists. "
            "Monitor neighboring fields for spread."
        ),
        "body_hi": (
            "गेहूँ में पीली रतुआ (Puccinia striiformis) मिली है। "
            "तुरंत प्रोपिकोनाज़ोल 25 EC 1 मिली प्रति लीटर या "
            "टेबुकोनाज़ोल 25.9 EC 1 मिली प्रति लीटर डालें। "
            "रोग जारी रहने पर 7-10 दिन के अंतराल पर छिड़काव करें। "
            "पड़ोसी खेतों में फैलाव की निगरानी करें।"
        ),
        "priority": AdvisoryPriority.urgent,
        "severity": SeverityLevel.high,
    },
    "powdery_mildew": {
        "title_en": "Powdery Mildew Detected",
        "title_hi": "चूर्णिल फफूंदी मिली",
        "body_en": (
            "Powdery mildew detected. "
            "Apply Sulphur 80 WP at 3g/L or Hexaconazole 5 SC at 2mL/L. "
            "Improve air circulation by reducing plant density. "
            "Avoid overhead irrigation."
        ),
        "body_hi": (
            "चूर्णिल फफूंदी मिली है। "
            "सल्फर 80 WP 3 ग्राम प्रति लीटर या हेक्साकोनाज़ोल 5 SC 2 मिली प्रति लीटर डालें। "
            "पौधों की घनत्व कम करके वायु संचार बढ़ाएं। "
            "ऊपरी सिंचाई से बचें।"
        ),
        "priority": AdvisoryPriority.high,
        "severity": SeverityLevel.medium,
    },
    "leaf_curl": {
        "title_en": "Leaf Curl Virus Detected",
        "title_hi": "पत्ती मुड़न वायरस मिला",
        "body_en": (
            "Leaf curl virus detected — spread by whiteflies. "
            "Remove and destroy infected plants immediately. "
            "Control whitefly with Imidacloprid 17.8 SL at 0.5mL/L. "
            "Install yellow sticky traps. Use silver reflective mulch."
        ),
        "body_hi": (
            "पत्ती मुड़न वायरस मिला है — सफेद मक्खी से फैलता है। "
            "संक्रमित पौधों को तुरंत हटाएं और नष्ट करें। "
            "इमिडाक्लोप्रिड 17.8 SL 0.5 मिली प्रति लीटर से सफेद मक्खी नियंत्रित करें। "
            "पीले चिपकने वाले जाल लगाएं। चांदी रंग की मल्च का उपयोग करें।"
        ),
        "priority": AdvisoryPriority.urgent,
        "severity": SeverityLevel.high,
    },
    "early_blight": {
        "title_en": "Early Blight Detected",
        "title_hi": "अगेती झुलसा रोग मिला",
        "body_en": (
            "Early blight (Alternaria solani) detected. "
            "Apply Mancozeb 75 WP at 2.5g/L or Chlorothalonil 75 WP at 2g/L. "
            "Remove lower infected leaves. Avoid overhead irrigation. "
            "Ensure adequate spacing between plants."
        ),
        "body_hi": (
            "अगेती झुलसा (Alternaria solani) मिला है। "
            "मैंकोज़ेब 75 WP 2.5 ग्राम प्रति लीटर या क्लोरोथेलोनिल 75 WP 2 ग्राम प्रति लीटर डालें। "
            "निचली संक्रमित पत्तियां हटाएं। ऊपरी सिंचाई से बचें। "
            "पौधों के बीच उचित दूरी सुनिश्चित करें।"
        ),
        "priority": AdvisoryPriority.high,
        "severity": SeverityLevel.medium,
    },
    "late_blight": {
        "title_en": "Late Blight — Urgent Action Required",
        "title_hi": "पछेती झुलसा — तुरंत कार्रवाई जरूरी",
        "body_en": (
            "Late blight (Phytophthora infestans) detected — extremely destructive. "
            "Apply Metalaxyl + Mancozeb 72 WP at 2.5g/L immediately. "
            "Spray every 5-7 days. Remove and burn infected material. "
            "Avoid touching healthy plants after handling infected ones. "
            "This disease can destroy the entire crop within 1-2 weeks."
        ),
        "body_hi": (
            "पछेती झुलसा (Phytophthora infestans) मिला है — अत्यंत विनाशकारी। "
            "तुरंत मेटालेक्सिल + मैंकोज़ेब 72 WP 2.5 ग्राम प्रति लीटर डालें। "
            "5-7 दिन के अंतराल पर छिड़काव करें। संक्रमित सामग्री हटाएं और जलाएं। "
            "संक्रमित पौधों को छूने के बाद स्वस्थ पौधों को न छुएं। "
            "यह रोग 1-2 सप्ताह में पूरी फसल नष्ट कर सकता है।"
        ),
        "priority": AdvisoryPriority.urgent,
        "severity": SeverityLevel.critical,
    },
    "aphid_infestation": {
        "title_en": "Aphid Infestation Detected",
        "title_hi": "माहू (एफिड) का प्रकोप मिला",
        "body_en": (
            "Aphid infestation detected. "
            "Apply Dimethoate 30 EC at 2mL/L or Thiamethoxam 25 WG at 0.5g/L. "
            "Spray the underside of leaves. Introduce natural predators like ladybugs. "
            "Install yellow sticky traps to monitor population."
        ),
        "body_hi": (
            "माहू (एफिड) का प्रकोप मिला है। "
            "डाइमेथोएट 30 EC 2 मिली प्रति लीटर या थियामेथोक्सम 25 WG 0.5 ग्राम प्रति लीटर डालें। "
            "पत्तियों की निचली सतह पर छिड़काव करें। लेडीबग जैसे प्राकृतिक शत्रु छोड़ें। "
            "जनसंख्या निगरानी के लिए पीले चिपकने वाले जाल लगाएं।"
        ),
        "priority": AdvisoryPriority.high,
        "severity": SeverityLevel.medium,
    },
    "whitefly": {
        "title_en": "Whitefly Infestation Detected",
        "title_hi": "सफेद मक्खी का प्रकोप मिला",
        "body_en": (
            "Whitefly infestation detected. "
            "Apply Imidacloprid 17.8 SL at 0.5mL/L or Acetamiprid 20 SP at 0.2g/L. "
            "Spray in early morning. Install yellow sticky traps. "
            "Whiteflies spread viruses — act quickly."
        ),
        "body_hi": (
            "सफेद मक्खी का प्रकोप मिला है। "
            "इमिडाक्लोप्रिड 17.8 SL 0.5 मिली प्रति लीटर या एसीटामिप्रिड 20 SP 0.2 ग्राम प्रति लीटर डालें। "
            "सुबह जल्दी छिड़काव करें। पीले चिपकने वाले जाल लगाएं। "
            "सफेद मक्खी वायरस फैलाती है — जल्दी कार्रवाई करें।"
        ),
        "priority": AdvisoryPriority.high,
        "severity": SeverityLevel.medium,
    },
    "mild_stress": {
        "title_en": "Mild Crop Stress Detected",
        "title_hi": "फसल में हल्का तनाव मिला",
        "body_en": (
            "Your crop shows mild stress. This may be due to water deficit, "
            "minor nutrient deficiency, or early pest activity. "
            "Check soil moisture and apply micronutrient spray (Zinc + Boron). "
            "Monitor closely over next 3-5 days."
        ),
        "body_hi": (
            "आपकी फसल में हल्का तनाव दिख रहा है। यह पानी की कमी, "
            "सूक्ष्म पोषक तत्व की कमी या कीट गतिविधि के कारण हो सकता है। "
            "मिट्टी की नमी जांचें और सूक्ष्म पोषक तत्व स्प्रे (जिंक + बोरोन) करें। "
            "अगले 3-5 दिनों तक नजर रखें।"
        ),
        "priority": AdvisoryPriority.medium,
        "severity": SeverityLevel.low,
    },
    "moderate_stress": {
        "title_en": "Moderate Crop Stress — Action Needed",
        "title_hi": "फसल में मध्यम तनाव — कार्रवाई जरूरी",
        "body_en": (
            "Your crop shows moderate stress. Immediate diagnosis is recommended. "
            "Check for nutrient deficiency (yellowing = N, purple = P, brown edges = K). "
            "Apply NPK foliar spray. Check irrigation schedule. "
            "If symptoms worsen, consult your local agriculture officer."
        ),
        "body_hi": (
            "आपकी फसल में मध्यम तनाव है। तुरंत निदान की जरूरत है। "
            "पोषक तत्व की कमी जांचें (पीलापन = N, बैंगनी = P, भूरे किनारे = K)। "
            "NPK पर्णीय स्प्रे करें। सिंचाई कार्यक्रम जांचें। "
            "लक्षण बिगड़ने पर स्थानीय कृषि अधिकारी से संपर्क करें।"
        ),
        "priority": AdvisoryPriority.high,
        "severity": SeverityLevel.medium,
    },
    "severe_stress": {
        "title_en": "Severe Crop Stress — Urgent Action Required",
        "title_hi": "फसल में गंभीर तनाव — तुरंत कार्रवाई जरूरी",
        "body_en": (
            "Your crop is under severe stress and may face significant yield loss. "
            "Contact your local Krishi Vigyan Kendra (KVK) immediately. "
            "Document the damage with photos for insurance purposes. "
            "Consider submitting an insurance claim through FasalSetu."
        ),
        "body_hi": (
            "आपकी फसल गंभीर तनाव में है और उपज में भारी नुकसान हो सकता है। "
            "तुरंत अपने स्थानीय कृषि विज्ञान केंद्र (KVK) से संपर्क करें। "
            "बीमा के लिए फोटो से नुकसान दर्ज करें। "
            "FasalSetu के माध्यम से बीमा दावा दाखिल करने पर विचार करें।"
        ),
        "priority": AdvisoryPriority.urgent,
        "severity": SeverityLevel.critical,
    },
}


def generate_advisory(
    disease_name: str,
    health_class: str,
    confidence: float,
) -> dict:
    """
    Generate a bilingual advisory based on detection results.
    Returns advisory dict with title_en, title_hi, body_en, body_hi, priority, severity.
    """
    # Disease-specific advisory takes priority over health class
    advisory_key = disease_name if disease_name in ADVISORY_DB else health_class
    advisory     = ADVISORY_DB.get(advisory_key, ADVISORY_DB["healthy"])

    logger.info(
        "Advisory generated",
        disease=disease_name,
        health_class=health_class,
        priority=advisory["priority"].value,
    )

    return {
        "title_en": advisory["title_en"],
        "title_hi": advisory["title_hi"],
        "body_en":  advisory["body_en"],
        "body_hi":  advisory["body_hi"],
        "priority": advisory["priority"],
        "severity": advisory["severity"],
    }