"""
Automated vision-based quality scoring against the 4-point rubric.

Rubric:
  1. Theme relevance
  2. Brand guideline adherence (colors, typography, logo usage)
  3. Logo accuracy (minor imperfections accepted -- not pixel-perfect)
  4. Jewelry realism -- ONLY checked if jewelry is actually rendered in the image
"""

import base64
from dataclasses import dataclass

from openai import OpenAI

client = OpenAI()


@dataclass
class ScoreResult:
    passed: bool
    reason: str  # short explanation -- used as retry_feedback if failed


RUBRIC_PROMPT_TEMPLATE = """You are reviewing a generated social media image for a jewellery brand.

Theme this image should match: {theme_name}
Content focus: {content_focus}

Check the image against these criteria:
1. Does the image clearly match the theme and content focus above?
2. Does it follow brand visual guidelines (colors, typography, logo usage)?
3. If a logo appears, is it reasonably close to correct? (minor imperfections are OK)
4. If actual jewelry is rendered in the image, does it look physically realistic
   (no impossible geometry, inverted earrings, broken clasps, etc.)?
   If there is no rendered jewelry in this image, skip this check entirely.

Respond with exactly one line in this format:
PASS or FAIL | <one sentence reason>
"""


def score_image(image_bytes: bytes, theme_name: str, content_focus: str) -> ScoreResult:
    """
    Sends the generated image + rubric to a vision-capable model and parses
    a pass/fail verdict with a reason.

    TODO: once you're running real generations, tune the rubric prompt
    wording based on where the scorer is too lenient or too strict.
    """
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    prompt = RUBRIC_PROMPT_TEMPLATE.format(theme_name=theme_name, content_focus=content_focus)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_image}"},
                    },
                ],
            }
        ],
    )

    raw = response.choices[0].message.content.strip()
    passed = raw.upper().startswith("PASS")
    reason = raw.split("|", 1)[1].strip() if "|" in raw else raw
    return ScoreResult(passed=passed, reason=reason)
