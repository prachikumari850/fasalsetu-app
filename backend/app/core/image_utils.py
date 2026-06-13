from PIL import Image
import imagehash
import io
import hashlib
from fastapi import UploadFile


async def read_image_bytes(file: UploadFile) -> bytes:
    """Read upload file bytes and reset position."""
    content = await file.read()
    await file.seek(0)
    return content


def compute_phash(image_bytes: bytes) -> str:
    """Compute perceptual hash of an image for duplicate detection."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("RGB")
        phash = str(imagehash.phash(img, hash_size=16))
        return phash
    except Exception:
        # Fallback to SHA256 if image cannot be opened
        return hashlib.sha256(image_bytes).hexdigest()[:32]


def validate_image(image_bytes: bytes, max_size_mb: int = 10) -> str | None:
    """
    Validate image file.
    Returns error message string or None if valid.
    """
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        return f"Image too large: {size_mb:.1f}MB. Max {max_size_mb}MB."

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        return None
    except Exception:
        return "Invalid image file. Please upload a JPEG or PNG."


def get_image_content_type(filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }.get(ext, "image/jpeg")