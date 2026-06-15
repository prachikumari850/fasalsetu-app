from app.core.supabase import get_supabase_admin
from app.core.image_utils import get_image_content_type
import structlog
import uuid
from datetime import datetime

logger = structlog.get_logger()


def upload_image_to_storage(
    bucket: str,
    user_id: str,
    image_bytes: bytes,
    original_filename: str,
) -> tuple[str, str]:
    supabase = get_supabase_admin()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    ext = original_filename.split(".")[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"

    file_path = f"{user_id}/{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"
    content_type = get_image_content_type(original_filename)

    try:
        supabase.storage.from_(bucket).upload(
            path=file_path,
            file=image_bytes,
            file_options={"content-type": content_type, "upsert": "false"},
        )
        signed = supabase.storage.from_(bucket).create_signed_url(
            path=file_path,
            expires_in=315_360_000,
        )
        url = signed.get("signedURL") or signed.get("signedUrl", "")
        logger.info("Image uploaded", bucket=bucket, path=file_path)
        return file_path, url
    except Exception as e:
        logger.error("Storage upload failed", error=str(e), path=file_path)
        raise RuntimeError(f"Failed to upload image: {str(e)}")