"""
Calls gpt-image-1 to generate the day's image -- either reference-conditioned
(images.edit, using catalogue photos) or pure text-to-image (images.generate).
"""

from pathlib import Path

from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env


def generate_with_reference(prompt: str, reference_image_paths: list[Path]) -> bytes:
    """
    Reference-conditioned generation via /v1/images/edits.
    Used for Tuesday (always) and Mon/Sat when a product is shown.
    Returns raw image bytes (decoded from base64).
    """
    files = [open(p, "rb") for p in reference_image_paths]
    try:
        result = client.images.edit(
            model="gpt-image-1",
            image=files,
            prompt=prompt,
        )
    finally:
        for f in files:
            f.close()

    import base64
    return base64.b64decode(result.data[0].b64_json)


def generate_text_to_image(prompt: str) -> bytes:
    """
    Pure text-to-image generation via /v1/images/generations.
    Used for Mon/Sat when no product reference is needed.
    Returns raw image bytes (decoded from base64).
    """
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
    )
    import base64
    return base64.b64decode(result.data[0].b64_json)
