
"""
CLIP-based crop image screening.

This module checks whether an uploaded image looks like a crop/plant
photograph or an unrelated object. It does not detect crop diseases.
"""

from io import BytesIO
import threading

import torch
from PIL import Image, UnidentifiedImageError
from transformers import CLIPModel, CLIPProcessor


MODEL_NAME = "openai/clip-vit-base-patch32"

# Conservative thresholds: uncertain images are sent for another upload.
CROP_THRESHOLD = 0.60
NON_CROP_THRESHOLD = 0.65
MIN_CONFIDENCE_GAP = 0.15

CROP_DESCRIPTION = (
    "A real photograph of agricultural crops growing in a farm field, "
    "showing crop plants, leaves, stems, or cultivated vegetation."
)

NON_CROP_DESCRIPTION = (
    "A photograph of an unrelated object or scene, such as a table, chair, "
    "desk, furniture, vehicle, building, document, or indoor room, "
    "with no agricultural crop plants as the main subject."
)

_model = None
_processor = None
_model_lock = threading.Lock()


def _load_model():
    """Load CLIP once and reuse it for subsequent images."""
    global _model, _processor

    if _model is None or _processor is None:
        with _model_lock:
            if _model is None or _processor is None:
                _processor = CLIPProcessor.from_pretrained(MODEL_NAME)
                _model = CLIPModel.from_pretrained(MODEL_NAME)
                _model.eval()

    return _model, _processor


def check_crop_image(image_bytes: bytes) -> dict:
    """
    Screen image bytes using CLIP.

    Returns:
        {
            "decision": "accepted" | "rejected" | "review",
            "crop_score": float,
            "non_crop_score": float,
            "message": str
        }
    """
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        return {
            "decision": "rejected",
            "crop_score": 0.0,
            "non_crop_score": 0.0,
            "message": "Unable to read the uploaded image.",
        }

    model, processor = _load_model()

    inputs = processor(
        text=[CROP_DESCRIPTION, NON_CROP_DESCRIPTION],
        images=image,
        return_tensors="pt",
        padding=True,
    )

    with torch.inference_mode():
        outputs = model(**inputs)
        probabilities = outputs.logits_per_image.softmax(dim=1)[0]

    crop_score = float(probabilities[0].item())
    non_crop_score = float(probabilities[1].item())
    confidence_gap = crop_score - non_crop_score

    if (
        crop_score >= CROP_THRESHOLD
        and confidence_gap >= MIN_CONFIDENCE_GAP
    ):
        decision = "accepted"
        message = "Crop image detected. Upload can continue."

    elif (
        non_crop_score >= NON_CROP_THRESHOLD
        and -confidence_gap >= MIN_CONFIDENCE_GAP
    ):
        decision = "rejected"
        message = "This does not appear to be a crop image. Please upload a crop photograph."

    else:
        decision = "review"
        message = "Image could not be confidently classified. Please upload a clearer crop photograph."

    return {
        "decision": decision,
        "crop_score": round(crop_score, 4),
        "non_crop_score": round(non_crop_score, 4),
        "message": message,
    }
