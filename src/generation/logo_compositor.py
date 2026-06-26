"""
Composites the real Santrea logo onto a generated image after generation.

Two decisions happen here:
1. SHAPE (logomark vs monogram) -- decided by a vision model call, since this
   depends on composition/available space, which isn't measurable by a
   simple pixel check.
2. COLOR (dark/light/gold) -- decided deterministically by measuring the
   actual brightness of the region the logo will sit on, so it stays legible
   regardless of what the AI generated underneath. Gold is reserved for
   manual override on special/festive themes, not auto-picked.
"""

import base64
import io
from pathlib import Path

from openai import OpenAI
from PIL import Image, ImageStat

client = OpenAI()

LOGO_DIR = Path("assets/logo")

LOGO_VARIANTS = {
    "logomark": {
        "dark": LOGO_DIR / "logomark_dark.png",
        "light": LOGO_DIR / "logomark_light.png",
        "gold": LOGO_DIR / "logomark_gold.png",
    },
    "monogram": {
        "dark": LOGO_DIR / "monogram_dark.png",
        "light": LOGO_DIR / "monogram_light.png",
        "gold": LOGO_DIR / "monogram_gold.png",
    },
}

BRIGHTNESS_THRESHOLD = 128  # 0-255; below this counts as a "dark" background

SHAPE_PROMPT = """You are choosing which logo shape fits best on this generated image, based on its composition and available negative space in the corner where a small logo must be placed.

Option A ("logomark"): a compact symbol mark. Best for tighter corners, busier backgrounds, or square/vertical compositions with limited clean space.
Option B ("monogram"): a stylized lettering mark. Best when there is a cleaner, more open area, or a more horizontal composition.

Look at the generated image first, then the two shape samples provided.

Respond with exactly one word: logomark or monogram
"""


def _encode(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def choose_logo_shape(image_bytes: bytes) -> str:
    """Ask a vision model to pick logomark vs monogram based on the image's composition."""
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    logomark_sample = _encode(LOGO_VARIANTS["logomark"]["dark"])
    monogram_sample = _encode(LOGO_VARIANTS["monogram"]["dark"])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SHAPE_PROMPT},
                    {"type": "text", "text": "Generated image:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}},
                    {"type": "text", "text": "Logomark shape sample:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{logomark_sample}"}},
                    {"type": "text", "text": "Monogram shape sample:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{monogram_sample}"}},
                ],
            }
        ],
    )

    answer = response.choices[0].message.content.strip().lower()
    return "monogram" if "monogram" in answer else "logomark"


def _region_brightness(base: Image.Image, box: tuple[int, int, int, int]) -> float:
    region = base.crop(box).convert("L")
    return ImageStat.Stat(region).mean[0]


def composite_logo(
    image_bytes: bytes,
    position: str = "bottom-right",
    logo_width_ratio: float = 0.12,
    margin_ratio: float = 0.04,
    shape_override: str | None = None,   # "logomark" | "monogram" -- skip AI shape pick
    color_override: str | None = None,   # "dark" | "light" | "gold" -- skip auto color pick
) -> bytes:
    """Overlay the real logo onto the generated image, auto-picking shape and contrast color."""
    base = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

    target_width = int(base.width * logo_width_ratio)
    margin = int(base.width * margin_ratio)

    positions = {
        "bottom-right": (base.width - target_width - margin, base.height - target_width - margin),
        "bottom-left": (margin, base.height - target_width - margin),
        "top-right": (base.width - target_width - margin, margin),
        "top-left": (margin, margin),
    }
    paste_x, paste_y = positions.get(position, positions["bottom-right"])

    shape = shape_override or choose_logo_shape(image_bytes)

    probe_logo = Image.open(LOGO_VARIANTS[shape]["dark"]).convert("RGBA")
    aspect = probe_logo.height / probe_logo.width
    target_height = int(target_width * aspect)

    region_box = (paste_x, paste_y, paste_x + target_width, paste_y + target_height)

    if color_override:
        chosen_color = color_override
    else:
        brightness = _region_brightness(base, region_box)
        chosen_color = "light" if brightness < BRIGHTNESS_THRESHOLD else "dark"

    logo_path = LOGO_VARIANTS[shape].get(chosen_color, LOGO_VARIANTS[shape]["dark"])
    logo = Image.open(logo_path).convert("RGBA").resize((target_width, target_height), Image.LANCZOS)

    base.paste(logo, (paste_x, paste_y), logo)

    output = io.BytesIO()
    base.convert("RGB").save(output, format="PNG")
    return output.getvalue()