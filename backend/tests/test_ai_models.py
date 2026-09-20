import io

from PIL import Image

from app.ai.disease_detector import DiseaseDetector
from app.ai.health_classifier import HealthClassifier
from app.core.image_utils import validate_image


def _jpeg_bytes() -> bytes:
    image = Image.new("RGB", (32, 32), color=(40, 140, 60))
    output = io.BytesIO()
    image.save(output, format="JPEG")
    return output.getvalue()


def test_image_validation_rejects_empty_and_non_images():
    assert validate_image(b'') == "The uploaded image is empty."
    assert validate_image(b'not an image') is not None


def test_real_onnx_models_accept_a_valid_image():
    image_bytes = _jpeg_bytes()
    detections = DiseaseDetector.get().detect(image_bytes)
    health = HealthClassifier.get().classify(image_bytes)

    assert isinstance(detections, list)
    assert health["class_name"] in HealthClassifier.get().config["class_names"]
    assert 0 <= health["confidence"] <= 1
    assert 0 <= health["health_score"] <= 100
