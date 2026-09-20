from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import structlog

from app.ai.disease_detector import DiseaseDetector
from app.ai.health_classifier import HealthClassifier
from app.ai.advisory_generator import generate_advisory
from app.models.crop import CropImage, DiseaseReport, Advisory, SeverityLevel
from app.core.storage import get_image_bytes_from_storage

logger = structlog.get_logger()


async def run_inference_pipeline(
    image_id: uuid.UUID,
    farm_id: uuid.UUID,
    image_bytes: bytes,
    db: AsyncSession,
) -> dict:
    """
    Complete AI inference pipeline for a single crop image.
    Runs in background after image upload.

    Flow:
      image_bytes
        → YOLOv8  → disease detections
        → EfficientNet → health classification
        → DiseaseReport saved to DB
        → Advisory generated and saved to DB
        → CropImage.ai_processed = True
    """
    logger.info("AI pipeline started", image_id=str(image_id))

    try:
        # Run both models (CPU-bound — run in thread pool)
        loop = asyncio.get_event_loop()

        disease_detector   = DiseaseDetector.get()
        health_classifier  = HealthClassifier.get()

        # Run in thread pool to avoid blocking async event loop
        detections, health_result = await asyncio.gather(
            loop.run_in_executor(None, disease_detector.detect, image_bytes),
            loop.run_in_executor(None, health_classifier.classify, image_bytes),
        )

        logger.info(
            "Inference complete",
            image_id=str(image_id),
            detections=len(detections),
            health_class=health_result["class_name"],
            health_score=health_result["health_score"],
        )

        # Determine primary disease (highest confidence, non-healthy)
        primary_detection = next(
            (d for d in detections if d["class_name"] != "healthy"),
            detections[0] if detections else {
                "class_name": "healthy",
                "confidence": 1.0,
                "bbox": None,
            },
        )

        disease_name = primary_detection["class_name"]
        confidence   = primary_detection["confidence"]
        bbox_data    = primary_detection.get("bbox")

        # Determine severity from health classification
        severity_map = {
            "healthy":         SeverityLevel.low,
            "mild_stress":     SeverityLevel.low,
            "moderate_stress": SeverityLevel.medium,
            "severe_stress":   SeverityLevel.critical,
        }
        severity = severity_map.get(health_result["class_name"], SeverityLevel.medium)

        # Override severity for specific critical diseases
        if disease_name in ("late_blight", "bacterial_blight"):
            severity = SeverityLevel.critical
        elif disease_name in ("leaf_blast", "yellow_rust", "leaf_curl"):
            severity = SeverityLevel.high

        # Save disease report
        disease_report = DiseaseReport(
            image_id=image_id,
            disease_name=disease_name,
            confidence=confidence,
            severity=severity,
            affected_area=None,
            bbox_data=bbox_data,
            model_version="yolov8n-v1",
            raw_output={
                "detections":   detections,
                "health":       health_result,
            },
            detected_at=datetime.now(timezone.utc),
        )
        db.add(disease_report)
        await db.flush()
        await db.refresh(disease_report)

        # Generate advisory
        advisory_data = generate_advisory(
            disease_name=disease_name,
            health_class=health_result["class_name"],
            confidence=confidence,
        )

        # Only create advisory if it's not just "healthy" with high confidence
        should_create_advisory = not (
            disease_name == "healthy"
            and health_result["class_name"] == "healthy"
            and health_result["health_score"] >= 85
        )

        advisory_id = None
        if should_create_advisory:
            advisory = Advisory(
                farm_id=farm_id,
                disease_report_id=disease_report.id,
                title_en=advisory_data["title_en"],
                title_hi=advisory_data["title_hi"],
                body_en=advisory_data["body_en"],
                body_hi=advisory_data["body_hi"],
                priority=advisory_data["priority"],
                is_read=False,
            )
            db.add(advisory)
            await db.flush()
            advisory_id = advisory.id

        # Mark image as processed
        result = await db.execute(
            __import__("sqlalchemy").select(CropImage).where(CropImage.id == image_id)
        )
        crop_image = result.scalar_one_or_none()
        if crop_image:
            crop_image.ai_processed = True
            await db.flush()

        await db.commit()

        logger.info(
            "AI pipeline complete",
            image_id=str(image_id),
            disease=disease_name,
            health_score=health_result["health_score"],
            severity=severity.value,
            advisory_created=advisory_id is not None,
        )

        return {
            "image_id":     str(image_id),
            "disease_name": disease_name,
            "confidence":   confidence,
            "severity":     severity.value,
            "health_score": health_result["health_score"],
            "health_class": health_result["class_name"],
            "detections":   detections,
            "advisory_created": advisory_id is not None,
            "disease_report_id": str(disease_report.id),
        }

    except Exception as e:
        logger.error(
            "AI pipeline failed",
            image_id=str(image_id),
            error=str(e),
        )
        # Keep ai_processed false.  Marking a failed inference as complete hid
        # real model/database failures from both the UI and future retries.
        try:
            await db.rollback()
        except Exception:
            pass
        raise
