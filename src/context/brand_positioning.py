"""
Loads the brand positioning document (voice, audience, messaging).
Feeds caption generation specifically -- not image generation.

TODO: point DEFAULT_PATH at your brand positioning doc.
"""

from pathlib import Path

DEFAULT_PATH = Path("assets/brand_positioning.md")


def load_brand_positioning(path: Path = DEFAULT_PATH) -> str:
    """Return the brand positioning doc as plain text, for caption generation."""
    if not path.exists():
        raise FileNotFoundError(
            f"Brand positioning doc not found at {path}. "
            "Add your positioning doc there, or pass a different path."
        )
    return path.read_text(encoding="utf-8")
