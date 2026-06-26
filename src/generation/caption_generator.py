"""
Generates the caption text for a piece of content, using brand positioning
+ theme context. Kept separate from image generation since it has a
different context input (positioning doc, not guidelines doc).
"""

from openai import OpenAI

client = OpenAI()


def generate_caption(prompt: str) -> str:
    """
    TODO: swap model name if you want to use a different text model.
    Keep this call simple -- a single prompt in, caption text out.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()
