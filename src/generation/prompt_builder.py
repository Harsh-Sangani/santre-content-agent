"""
Builds the image-generation prompt from theme + brand voice + (optional) product context.

Content is posted to a WhatsApp Community/group, not Instagram -- prompts
avoid platform mechanics that don't apply there (hashtags, comments,
"link in bio", swipe-up, follow-us CTAs, etc.).
"""

from src.config.themes import DayTheme

# Shared instruction to avoid common "obviously AI-written" tells in any
# generated text (captions and poll suggestions). Applied to both prompt
# builders below.
HUMAN_TONE_INSTRUCTION = (
    "Write like an actual person typing a message in a WhatsApp group -- not "
    "like marketing copy or an AI assistant. Avoid generic phrases like "
    "'elevate your style', 'indulge in', 'discover the beauty of', "
    "'unlock', 'timeless elegance', or any opening like 'Imagine...'. "
    "Do not use em dashes. Avoid excessive exclamation points or emoji. "
    "Vary sentence length and structure naturally, the way a real person "
    "writes -- not uniform, polished marketing sentences. It's fine to be "
    "a little casual or imperfect. Say something specific and real rather "
    "than vague enthusiasm."
)


def build_image_prompt(
    theme: DayTheme,
    brand_guidelines: str,
    has_product_reference: bool,
    retry_feedback: str | None = None,
) -> str:
    """
    Construct the prompt sent to gpt-image-2.

    retry_feedback: if this is a retry after a failed quality score, pass the
    scorer's failure reason here so the next attempt corrects for it instead
    of repeating the same mistake blindly.

    TODO: tune this prompt template against real output once you're running
    actual generations -- this is a first-pass structure, not a final prompt.
    """
    base = (
        f"Create a square image for a jewellery brand to be shared as a post "
        f"in a WhatsApp community/group. Theme: {theme.theme_name}. "
        f"Content focus: {theme.content_focus} "
        f"Follow these brand visual guidelines strictly: {brand_guidelines} "
        f"Do not render any logo, brand mark, or brand wordmark anywhere in "
        f"the image -- leave a clean, uncluttered area in the bottom-right "
        f"corner; the logo will be added separately afterward. "
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


def build_poll_prompt(
    theme: DayTheme,
    brand_positioning: str,
    retry_feedback: str | None = None,
) -> str:
    """
    Construct the prompt for days using output_format="poll".

    The result is NOT a message -- it's a question + 2-4 short options meant
    to be copied directly into WhatsApp's native "Create Poll" feature, used
    alongside the generated image (not embedded in it).

    The image itself is passed alongside this prompt (see caption_generator.
    generate_poll) so the question/options are grounded in what is actually
    shown -- not invented independently of the visual.
    """
    base = (
        f"Look at the provided image first. Suggest a short, engaging poll "
        f"for a jewellery brand's WhatsApp community, to be used in "
        f"WhatsApp's native poll feature alongside this exact image. "
        f"Theme: {theme.theme_name}. Content focus: {theme.content_focus} "
        f"Brand voice and positioning to follow: {brand_positioning} "
        f"The question and options must directly correspond to what is "
        f"actually depicted in the image -- if the image shows specific "
        f"styles, pieces, or visual choices, the poll options must reference "
        f"those same things, not unrelated alternatives. If the image shows "
        f"only one piece or a general scene rather than distinct choices, "
        f"write a poll question that fits that (e.g. a preference or opinion "
        f"question), not a forced multi-option comparison that isn't shown. "
        f"{HUMAN_TONE_INSTRUCTION} "
        f"Output in exactly this format, nothing else:\n"
        f"Poll question: <one short question>\n"
        f"Options:\n"
        f"1. <short option>\n"
        f"2. <short option>\n"
        f"3. <short option, optional>\n"
        f"4. <short option, optional>\n"
        f"Keep the question and each option short enough to read at a glance "
        f"in a poll UI -- options should be a few words, not full sentences."
    )
    if retry_feedback:
        base += f"\nPrevious attempt was rejected for this reason, correct for it: {retry_feedback}"
    return base


def build_caption_prompt(theme: DayTheme, brand_positioning: str) -> str:
    """Construct the prompt sent to the text model for the message accompanying the image."""
    return (
        f"Write the message text that will accompany an image posted to a "
        f"WhatsApp community/group for a jewellery brand. This is NOT an "
        f"Instagram caption -- there are no comments, no hashtags, no "
        f"'link in bio', no follow/like mechanics, and no swipe-up. Write it "
        f"as a natural, direct message someone would actually send in a "
        f"WhatsApp broadcast. "
        f"Theme: {theme.theme_name}. Content focus: {theme.content_focus} "
        f"Brand voice and positioning to follow: {brand_positioning} "
        f"{HUMAN_TONE_INSTRUCTION} "
        f"Keep it concise and on-brand. If a call to action makes sense, "
        f"phrase it for WhatsApp -- e.g. inviting a reply in the group, or "
        f"pointing to the website -- never an Instagram-specific action."
    )