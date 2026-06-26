"""
Generates the text accompanying a piece of content (caption or poll).

Vision-aware: sees the actual generated image so the text is grounded in
what's actually depicted (correct product type, style, etc.) rather than
invented independently of the visual.
"""

import base64

from openai import OpenAI

client = OpenAI()


def generate_text(image_bytes: bytes, prompt: str) -> str:
    """
    Generates text with the image included, so the output is grounded in
    what's actually shown -- used for both normal captions and poll
    suggestions, since both need to match what's actually in the image.
    """
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

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
    return response.choices[0].message.content.strip()