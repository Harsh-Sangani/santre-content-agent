"""
Generates the text accompanying a piece of content.

generate_caption: plain text-only generation (used for Monday/Tuesday message text).
generate_poll: vision-aware generation (used for Saturday's poll-format output) --
sees the actual generated image so the poll question/options are grounded in
what's depicted, rather than invented independently of the visual.
"""

import base64

from openai import OpenAI

client = OpenAI()


def generate_caption(prompt: str) -> str:
    """
    TODO: swap model name if you want to use a different text model.
    Keep this call simple -- a single prompt in, text out.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def generate_poll(image_bytes: bytes, prompt: str) -> str:
    """
    Generates poll question + options, with the image included so the
    output is grounded in what's actually shown -- not generated blind.
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