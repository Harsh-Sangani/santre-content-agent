"""
Builds the image-generation prompt from theme + brand voice + (optional) product context.
"""

from src.config.themes import DayTheme


def build_image_prompt(
    theme: DayTheme,
    brand_guidelines: str,
    has_product_reference: bool,
    retry_feedback: str | None = None,
) -> str:
    """
    Construct the prompt sent to gpt-image-1.

    retry_feedback: if this is a retry after a failed quality score, pass the
    scorer's failure reason here so the next attempt corrects for it instead
    of repeating the same mistake blindly.

    TODO: tune this prompt template against real output once you're running
    actual generations -- this is a first-pass structure, not a final prompt.
    """
    base = (
        f"Create a square Instagram post image for a jewellery brand. "
        f"Theme: {theme.theme_name}. Content focus: {theme.content_focus} "
        f"Follow these brand visual guidelines strictly: {brand_guidelines} "
    )
    if has_product_reference:
        base += (
            "Use the provided reference product photo(s) as the actual jewellery "
            "shown -- do not invent new jewellery geometry, edit/compose around "
            "the real product image(s) provided. "
        )
    else:
        base += "No specific product needs to be rendered; focus on the theme. "

    if retry_feedback:
        base += f"Previous attempt was rejected for this reason, correct for it: {retry_feedback} "

    return base.strip()


def build_caption_prompt(theme: DayTheme, brand_positioning: str) -> str:
    """Construct the prompt sent to the text model for caption generation."""
    return (
        f"Write an Instagram caption for a jewellery brand post. "
        f"Theme: {theme.theme_name}. Content focus: {theme.content_focus} "
        f"Brand voice and positioning to follow: {brand_positioning} "
        f"Keep it concise, on-brand, and include a natural call to action."
    )
