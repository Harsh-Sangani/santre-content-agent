"""
Runs the full weekly pipeline: for each configured day, build context,
generate + score + retry the image, generate the caption, and write
output to Drive + Sheets.

This is the entry point GitHub Actions calls on the Sunday 9am cron.
"""

import datetime
import os

from src.config.themes import THEME_CONFIG
from src.context.brand_guidelines import load_brand_guidelines
from src.context.brand_positioning import load_brand_positioning
from src.context.catalogue import pick_reference_images_for_theme
from src.generation.caption_generator import generate_caption
from src.generation.image_generator import generate_text_to_image, generate_with_reference
from src.generation.prompt_builder import build_caption_prompt, build_image_prompt
from src.output.drive_uploader import get_or_create_week_folder, upload_image
from src.output.sheets_writer import append_row, create_week_tab
from src.review.scorer import score_image

MAX_RETRIES = 3
IMAGE_QUALITY = "high"  # "low" | "medium" | "high" — drop to "medium" once prompts are stable


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

    caption_prompt = build_caption_prompt(theme, brand_positioning)
    caption = generate_caption(caption_prompt)

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


def main():
    brand_guidelines = load_brand_guidelines()
    brand_positioning = load_brand_positioning()

    today = datetime.date.today()
    week_label = f"Week_{today.isoformat()}"

    parent_folder_id = os.environ["GOOGLE_DRIVE_PARENT_FOLDER_ID"]
    spreadsheet_id = os.environ["GOOGLE_SHEETS_SPREADSHEET_ID"]

    drive_folder_id = get_or_create_week_folder(week_label, parent_folder_id)
    create_week_tab(spreadsheet_id, week_label)

    for theme in THEME_CONFIG:
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
