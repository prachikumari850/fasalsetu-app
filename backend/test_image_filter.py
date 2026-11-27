
from pathlib import Path

from app.ai.image_filter import check_crop_image

# Put your test images inside backend/test_images/
test_folder = Path("test_images")

for image_path in test_folder.iterdir():
    if image_path.suffix.lower() not in {
        ".jpg", ".jpeg", ".png", ".webp"
    }:
        continue

    result = check_crop_image(image_path.read_bytes())

    print("\nImage:", image_path.name)
    print("Decision:", result["decision"])
    print("Crop score:", result["crop_score"])
    print("Non-crop score:", result["non_crop_score"])
    print("Message:", result["message"])
