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
    
    
def get_image_bytes_from_storage(storage_path: str) -> bytes:
    """
    Download image bytes from Supabase Storage for AI inference.
    """
    supabase = get_supabase_admin()

    # Determine bucket from path
    bucket = "crop-images"
    if "claim" in storage_path:
        bucket = "claim-images"

    try:
        response = supabase.storage.from_(bucket).download(storage_path)
        return response
    except Exception as e:
        logger.error("Failed to download image from storage",
                     path=storage_path, error=str(e))
        raise RuntimeError(f"Could not retrieve image: {str(e)}")