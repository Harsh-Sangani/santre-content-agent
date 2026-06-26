"""
Automated vision-based quality scoring.

score_image: the 4-point image rubric (theme relevance, brand guidelines,
no AI-drawn logo, jewelry realism).

check_poll_alignment: a separate check used only for poll-format days --
confirms the suggested poll question/options actually correspond to what's
depicted in the image, rather than describing options that aren't shown.
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
2. Does it follow brand visual guidelines (colors, typography)?
3. The image should NOT contain any logo, brand mark, or brand wordmark --
   the real logo gets added separately after this check. If one appears
   anyway, treat it as a failure.
4. If actual jewelry is rendered in the image, does it look physically realistic
   (no impossible geometry, inverted earrings, broken clasps, etc.)?
   If there is no rendered jewelry in this image, skip this check entirely.

Respond with exactly one line in this format:
PASS or FAIL | <one sentence reason>
"""

POLL_ALIGNMENT_PROMPT_TEMPLATE = """You are reviewing whether a suggested WhatsApp poll matches the image it will be posted alongside.

Suggested poll text:
{poll_text}

Check: does the poll question and do its options correspond to what is
actually depicted in the image? For example, if the image shows specific
distinct items, styles, or choices, the poll options must reference those
same things -- not different or unrelated alternatives. If the image shows
a single piece or general scene (not distinct choices), the poll should
still make sense as a general preference/opinion question relative to what's
shown, not reference options that aren't visually present at all.

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


def check_poll_alignment(image_bytes: bytes, poll_text: str) -> ScoreResult:
    """
    Confirms the suggested poll question/options correspond to what's
    actually shown in the image, catching cases like the image showing
    option A/B while the poll suggests unrelated C/D.
    """
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    prompt = POLL_ALIGNMENT_PROMPT_TEMPLATE.format(poll_text=poll_text)

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