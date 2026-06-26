"""
Loads product photos directly from a manually-curated catalogue folder,
for use as reference images in gpt-image-2's /images/edits endpoint.
"""

from pathlib import Path

CATALOGUE_DIR = Path("assets/catalogue")


def pick_reference_images_for_theme(
    theme_name: str,
    category: str | None = None,
    max_images: int = 3,
) -> list[Path]:
    """
    Pick relevant catalogue reference images.

    If category is given (e.g. "ring", "necklace"), filters filenames
    containing that string. Otherwise picks from the full folder.
    """
    available = sorted(CATALOGUE_DIR.glob("*.jpg")) + sorted(CATALOGUE_DIR.glob("*.png"))

    if category:
        available = [p for p in available if category.lower() in p.stem.lower()]

    return available[:max_images]