from __future__ import annotations
import io
import numpy as np
from PIL import Image
import onnxruntime as ort
from app.ai.model_config import EFFICIENTNET_MODEL_PATH, get_efficientnet_config
import structlog

logger = structlog.get_logger()


class HealthClassifier:
    """
    EfficientNet-B2 ONNX inference engine for crop health classification.
    Singleton pattern — model loaded once at startup.
    """

    _instance: "HealthClassifier | None" = None

    def __init__(self) -> None:
        self.config  = get_efficientnet_config()
        self.session: ort.InferenceSession | None = None
        self._load_model()

    @classmethod
    def get(cls) -> "HealthClassifier":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model(self) -> None:
        if not EFFICIENTNET_MODEL_PATH.exists():
            logger.error(
                "EfficientNet ONNX model not found",
                path=str(EFFICIENTNET_MODEL_PATH),
            )
            self.session = None
            raise RuntimeError("EfficientNet model file is missing")

        providers = ["CPUExecutionProvider"]
        self.session = ort.InferenceSession(
            str(EFFICIENTNET_MODEL_PATH),
            providers=providers,
        )
        logger.info(
            "EfficientNet model loaded",
            version=self.config["model_version"],
            path=str(EFFICIENTNET_MODEL_PATH),
        )

    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        size   = self.config["input_size"]
        mean   = np.array(self.config["normalize_mean"], dtype=np.float32)
        std    = np.array(self.config["normalize_std"],  dtype=np.float32)

        img    = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img    = img.resize((size, size), Image.BILINEAR)
        arr    = np.array(img, dtype=np.float32) / 255.0
        arr    = (arr - mean) / std
        arr    = arr.transpose(2, 0, 1)
        arr    = np.expand_dims(arr, axis=0)
        return arr.astype(np.float32)

    def _score_from_class(
        self,
        class_name: str,
        confidence: float,
    ) -> int:
        """
        Convert class name + confidence into a 0-100 health score.
        Higher confidence in a worse class → lower score.
        """
        score_map = self.config["health_score_map"]
        bounds    = score_map.get(class_name, {"min": 0, "max": 100})
        low, high = bounds["min"], bounds["max"]
        # Interpolate within the class range based on confidence
        score = int(low + (high - low) * confidence)
        return max(0, min(100, score))

    def classify(self, image_bytes: bytes) -> dict:
        """
        Run health classification on image bytes.
        Returns dict with class_name, confidence, health_score, all_probs.
        """
        if self.session is None:
            raise RuntimeError("EfficientNet model is not available")

        try:
            inp        = self._preprocess(image_bytes)
            input_name = self.session.get_inputs()[0].name
            output     = self.session.run(None, {input_name: inp})[0][0]

            # Softmax
            exp_output = np.exp(output - np.max(output))
            probs      = exp_output / exp_output.sum()

            class_id   = int(np.argmax(probs))
            confidence = float(probs[class_id])
            class_names = self.config["class_names"]
            class_name  = class_names[class_id]
            health_score = self._score_from_class(class_name, confidence)

            return {
                "class_id":     class_id,
                "class_name":   class_name,
                "confidence":   round(confidence, 4),
                "health_score": health_score,
                "all_probs": {
                    name: round(float(p), 4)
                    for name, p in zip(class_names, probs)
                },
            }
        except Exception as e:
            logger.error("EfficientNet inference failed", error=str(e))
            raise RuntimeError("EfficientNet inference failed") from e
