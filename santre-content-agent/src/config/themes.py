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


THEME_CONFIG: list[DayTheme] = [
    DayTheme(
        day="Monday",
        theme_name="Diamond Education",
        content_focus="Teach something valuable about diamonds (4Cs, cut types, care tips, certifications).",
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
        theme_name="Poll / Engagement",
        content_focus="Ask a question that invites comments/engagement related to jewellery preferences.",
        needs_product_reference=False,
        rubric_realism_check="conditional",
    ),
]
