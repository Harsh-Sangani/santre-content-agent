"""
Runs the full weekly pipeline: for each configured day, build context,
generate + score + retry the image, generate the caption (or, for
output_format="poll" days, generate + check-align + retry a poll
suggestion grounded in the image), and write output to Drive + Sheets.

This is the entry point GitHub Actions calls on the Sunday 9am cron.
"""
from dotenv import load_dotenv
load_dotenv()

import dataclasses
import datetime
import os

from src.config.themes import THEME_CONFIG
from src.context.brand_guidelines import load_brand_guidelines
from src.context.brand_positioning import load_brand_positioning
from src.context.catalogue import pick_reference_images_for_theme
from src.generation.caption_generator import generate_text
from src.generation.image_generator import generate_text_to_image, generate_with_reference
from src.generation.logo_compositor import composite_logo
from src.generation.prompt_builder import build_caption_prompt, build_image_prompt, build_poll_prompt
from src.output.drive_uploader import get_or_create_week_folder, upload_image
from src.output.sheets_writer import append_row, create_week_tab
from src.review.scorer import check_poll_alignment, score_image

MAX_RETRIES = 3
POLL_MAX_RETRIES = 2
IMAGE_QUALITY = "high"  # "low" | "medium" | "high" — drop to "medium" once prompts are stable


def _resolve_theme_for_week(theme, week_number: int):
    """
    If a theme has multiple content_angles defined, deterministically rotate
    through them by ISO week number so the same angle doesn't get picked
    every run -- avoids the AI defaulting to whichever angle is mentioned
    most prominently in content_focus.
    """
    if not theme.content_angles:
        return theme

    angle = theme.content_angles[week_number % len(theme.content_angles)]
    return dataclasses.replace(theme, content_focus=angle)


def run_day(theme, brand_guidelines: str, brand_positioning: str, drive_folder_id: str):
    """Run the full generate -> score -> retry -> caption -> package flow for one day."""
    reference_images = (
        pick_reference_images_for_theme(theme.theme_name) if theme.needs_product_reference else []
    )
    has_reference = len(reference_images) > 0

    retry_feedback = None
    image_bytes = None
    status = "Flagged"
    attempt = 0

    for attempt in range(1, MAX_RETRIES + 1):
        prompt = build_image_prompt(
            theme=theme,
            brand_guidelines=brand_guidelines,
            has_product_reference=has_reference,
            retry_feedback=retry_feedback,
        )

        image_bytes = (
            generate_with_reference(prompt, reference_images, quality=IMAGE_QUALITY)
            if has_reference
            else generate_text_to_image(prompt, quality=IMAGE_QUALITY)
        )

        score = score_image(image_bytes, theme.theme_name, theme.content_focus)
        if score.passed:
            status = "Approved"
            break
        retry_feedback = score.reason

    if status == "Approved":
        image_bytes = composite_logo(image_bytes)

    if theme.output_format == "poll":
        caption, poll_status = _generate_poll_with_alignment_check(image_bytes, theme, brand_positioning)
        if poll_status == "Flagged" and status == "Approved":
            status = "Approved (poll flagged for manual check)"
    else:
        caption_prompt = build_caption_prompt(theme, brand_positioning)
        caption = generate_text(image_bytes, caption_prompt)

    filename = f"{theme.day}.png"
    image_link = upload_image(image_bytes, filename, drive_folder_id)

    return {
        "day": theme.day,
        "theme": theme.theme_name,
        "image_link": image_link,
        "caption": caption,
        "status": status,
        "retry_count": attempt,
    }


def _generate_poll_with_alignment_check(image_bytes, theme, brand_positioning):
    """
    Generates a poll grounded in the image, then verifies alignment between
    the suggested options and what's actually shown. Retries the poll text
    (not the image) on misalignment, since the image is already approved.
    """
    retry_feedback = None
    poll_text = ""

    for attempt in range(1, POLL_MAX_RETRIES + 1):
        prompt = build_poll_prompt(theme, brand_positioning, retry_feedback=retry_feedback)
        poll_text = generate_text(image_bytes, prompt)

        alignment = check_poll_alignment(image_bytes, poll_text)
        if alignment.passed:
            return poll_text, "Approved"
        retry_feedback = alignment.reason

    return poll_text, "Flagged"


def main():
    brand_guidelines = load_brand_guidelines()
    brand_positioning = load_brand_positioning()

    today = datetime.date.today()
    week_label = f"Week_{today.isoformat()}"
    week_number = today.isocalendar()[1]

    parent_folder_id = os.environ["GOOGLE_DRIVE_PARENT_FOLDER_ID"]
    spreadsheet_id = os.environ["GOOGLE_SHEETS_SPREADSHEET_ID"]

    drive_folder_id = get_or_create_week_folder(week_label, parent_folder_id)
    create_week_tab(spreadsheet_id, week_label)

    for raw_theme in THEME_CONFIG:
        theme = _resolve_theme_for_week(raw_theme, week_number)
        result = run_day(theme, brand_guidelines, brand_positioning, drive_folder_id)
        append_row(
            spreadsheet_id,
            week_label,
            [
                result["day"],
                result["theme"],
                result["image_link"],
                result["caption"],
                result["status"],
                str(result["retry_count"]),
            ],
        )
        print(f"{result['day']}: {result['status']} (attempts: {result['retry_count']})")


if __name__ == "__main__":
    main()