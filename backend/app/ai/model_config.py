from pathlib import Path
import json

# Base path for trained models
# In development: ai-models/trained/ relative to repo root
# In production (Render): models are uploaded as part of deployment
MODELS_BASE = Path(__file__).parent.parent.parent / "models"


def get_yolo_config() -> dict:
    config_path = MODELS_BASE / "yolov8" / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    # Fallback defaults if model not yet trained
    return {
        "model_name": "FasalSetu Disease Detector v1",
        "model_version": "yolov8n-v1",
        "num_classes": 11,
        "class_names": [
            "healthy", "leaf_blast", "brown_spot", "bacterial_blight",
            "yellow_rust", "powdery_mildew", "leaf_curl",
            "early_blight", "late_blight", "aphid_infestation", "whitefly",
        ],
        "confidence_threshold": 0.4,
        "iou_threshold": 0.45,
        "input_size": 640,
    }


def get_efficientnet_config() -> dict:
    config_path = MODELS_BASE / "efficientnet" / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {
        "model_name": "FasalSetu Health Classifier v1",
        "model_version": "efficientnet_b2-v1",
        "num_classes": 4,
        "class_names": ["healthy", "mild_stress", "moderate_stress", "severe_stress"],
        "input_size": 224,
        "normalize_mean": [0.485, 0.456, 0.406],
        "normalize_std":  [0.229, 0.224, 0.225],
        "health_score_map": {
            "healthy":         {"min": 85, "max": 100},
            "mild_stress":     {"min": 60, "max": 84},
            "moderate_stress": {"min": 35, "max": 59},
            "severe_stress":   {"min": 0,  "max": 34},
        },
    }


YOLO_MODEL_PATH = MODELS_BASE / "yolov8" / "disease_detection_best.onnx"
EFFICIENTNET_MODEL_PATH = MODELS_BASE / "efficientnet" / "health_classifier_best.onnx"