"""
Day -> theme configuration for the content agent.

v1 scope: 3 days/week only. Add more entries here later to scale to 7.
"""

from dataclasses import dataclass


@dataclass
class DayTheme:
    day: str
    theme_name: str
    content_focus: str
    needs_product_reference: bool  # True = always pull a catalogue image as reference
    rubric_realism_check: str      # "always" | "conditional" | "never"
    output_format: str = "message"  # "message" | "poll" -- poll = question + options for WhatsApp's native poll feature


THEME_CONFIG: list[DayTheme] = [
    DayTheme(
        day="Monday",
        theme_name="Diamond Education",
        content_focus=(
            "Teach something valuable about diamonds. Lean into Santrea's "
            "unbiased natural-vs-lab-grown positioning where relevant -- not "
            "just generic 4Cs content."
        ),
        needs_product_reference=False,
        rubric_realism_check="conditional",
    ),
    DayTheme(
        day="Tuesday",
        theme_name="Jewellery Inspiration",
        content_focus="Showcase a beautiful design from the catalogue in an aspirational way.",
        needs_product_reference=True,
        rubric_realism_check="always",
    ),
    DayTheme(
        day="Saturday",
        theme_name="Engagement",
        content_focus=(
            "Create a visually engaging image related to jewellery preferences "
            "or style choices that pairs with a question for the audience."
        ),
        needs_product_reference=False,
        rubric_realism_check="conditional",
        output_format="poll",
    ),
]