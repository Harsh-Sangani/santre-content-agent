"""
Loads the brand guidelines document (visual rules: colors, typography, logo usage).

TODO: point DEFAULT_PATH at your condensed 5-page brand guidelines doc once it's
finalized. Accepts .md or .txt for now -- add a docx/pdf reader here if needed.
"""

from pathlib import Path

DEFAULT_PATH = Path("assets/brand_guidelines.md")


def load_brand_guidelines(path: Path = DEFAULT_PATH) -> str:
    """Return the brand guidelines as plain text, to be injected into prompts."""
    if not path.exists():
        raise FileNotFoundError(
            f"Brand guidelines not found at {path}. "
            "Add your guidelines doc there, or pass a different path."
        )
    return path.read_text(encoding="utf-8")
