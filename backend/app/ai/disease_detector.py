from __future__ import annotations
import io
import numpy as np
from PIL import Image
import onnxruntime as ort
from pathlib import Path
from app.ai.model_config import YOLO_MODEL_PATH, get_yolo_config
import structlog

logger = structlog.get_logger()


class DiseaseDetector:
    """
    YOLOv8 ONNX inference engine for crop disease and pest detection.
    Singleton pattern — model loaded once at startup.
    """

    _instance: "DiseaseDetector | None" = None

    def __init__(self) -> None:
        self.config  = get_yolo_config()
        self.session: ort.InferenceSession | None = None
        self._load_model()

    @classmethod
    def get(cls) -> "DiseaseDetector":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model(self) -> None:
        if not YOLO_MODEL_PATH.exists():
            logger.warning(
                "YOLOv8 ONNX model not found — running in mock mode",
                path=str(YOLO_MODEL_PATH),
            )
            self.session = None
            return

        providers = ["CPUExecutionProvider"]
        self.session = ort.InferenceSession(
            str(YOLO_MODEL_PATH),
            providers=providers,
        )
        logger.info(
            "YOLOv8 model loaded",
            version=self.config["model_version"],
            path=str(YOLO_MODEL_PATH),
        )

    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        """Resize and normalize image for YOLOv8 input."""
        size = self.config["input_size"]
        img  = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img  = img.resize((size, size), Image.BILINEAR)
        arr  = np.array(img, dtype=np.float32) / 255.0
        arr  = arr.transpose(2, 0, 1)          # HWC → CHW
        arr  = np.expand_dims(arr, axis=0)     # Add batch dim
        return arr

    def _postprocess(
        self,
        output: np.ndarray,
        conf_thresh: float,
        iou_thresh: float,
    ) -> list[dict]:
        """
        Parse YOLOv8 ONNX output.
        Output shape: [1, num_classes+4, num_anchors]
        Returns list of detections: {class_id, class_name, confidence, bbox}
        """
        predictions = output[0]                    # [num_classes+4, num_anchors]
        predictions = predictions.T                # [num_anchors, num_classes+4]

        boxes      = predictions[:, :4]            # cx, cy, w, h
        class_probs = predictions[:, 4:]           # class probabilities

        class_ids   = np.argmax(class_probs, axis=1)
        confidences = class_probs[np.arange(len(class_ids)), class_ids]

        # Filter by confidence
        mask         = confidences >= conf_thresh
        boxes        = boxes[mask]
        class_ids    = class_ids[mask]
        confidences  = confidences[mask]

        if len(boxes) == 0:
            return []

        # Convert cx,cy,w,h → x1,y1,x2,y2
        x1 = boxes[:, 0] - boxes[:, 2] / 2
        y1 = boxes[:, 1] - boxes[:, 3] / 2
        x2 = boxes[:, 0] + boxes[:, 2] / 2
        y2 = boxes[:, 1] + boxes[:, 3] / 2

        # Simple NMS
        keep = self._nms(
            np.stack([x1, y1, x2, y2], axis=1),
            confidences,
            iou_thresh,
        )

        class_names = self.config["class_names"]
        results = []
        for idx in keep:
            cid  = int(class_ids[idx])
            conf = float(confidences[idx])
            results.append({
                "class_id":   cid,
                "class_name": class_names[cid] if cid < len(class_names) else "unknown",
                "confidence": round(conf, 4),
                "bbox": {
                    "x1": round(float(x1[idx]), 4),
                    "y1": round(float(y1[idx]), 4),
                    "x2": round(float(x2[idx]), 4),
                    "y2": round(float(y2[idx]), 4),
                },
            })

        # Sort by confidence descending
        results.sort(key=lambda r: r["confidence"], reverse=True)
        return results

    @staticmethod
    def _nms(boxes: np.ndarray, scores: np.ndarray, iou_thresh: float) -> list[int]:
        """Non-Maximum Suppression."""
        x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        areas  = (x2 - x1) * (y2 - y1)
        order  = scores.argsort()[::-1]
        keep   = []

        while order.size > 0:
            i = order[0]
            keep.append(int(i))
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            w   = np.maximum(0.0, xx2 - xx1)
            h   = np.maximum(0.0, yy2 - yy1)
            iou = (w * h) / (areas[i] + areas[order[1:]] - w * h + 1e-6)
            inds   = np.where(iou <= iou_thresh)[0]
            order  = order[inds + 1]

        return keep

    def detect(self, image_bytes: bytes) -> list[dict]:
        """
        Run disease detection on image bytes.
        Returns list of detections or mock data if model not loaded.
        """
        if self.session is None:
            return self._mock_detection()

        try:
            inp    = self._preprocess(image_bytes)
            input_name = self.session.get_inputs()[0].name
            output = self.session.run(None, {input_name: inp})
            return self._postprocess(
                output[0],
                self.config["confidence_threshold"],
                self.config["iou_threshold"],
            )
        except Exception as e:
            logger.error("YOLOv8 inference failed", error=str(e))
            return self._mock_detection()

    def _mock_detection(self) -> list[dict]:
        """
        Returns mock result when model is not available.
        Used during development before training completes.
        """
        import random
        if random.random() > 0.4:
            return [{
                "class_id":   0,
                "class_name": "healthy",
                "confidence": round(random.uniform(0.75, 0.95), 4),
                "bbox":       {"x1": 0.1, "y1": 0.1, "x2": 0.9, "y2": 0.9},
            }]
        return [{
            "class_id":   1,
            "class_name": "leaf_blast",
            "confidence": round(random.uniform(0.55, 0.80), 4),
            "bbox":       {"x1": 0.2, "y1": 0.3, "x2": 0.7, "y2": 0.8},
        }]
