"""
Day -> theme configuration for the content agent.

v1 scope: 3 days/week only. Add more entries here later to scale to 7.
"""

from dataclasses import dataclass, field


@dataclass
class DayTheme:
    day: str
    theme_name: str
    content_focus: str
    needs_product_reference: bool  # True = always pull a catalogue image as reference
    rubric_realism_check: str      # "always" | "conditional" | "never"
    output_format: str = "message"  # "message" | "poll" -- poll = question + options for WhatsApp's native poll feature
    content_angles: list[str] = field(default_factory=list)  # if set, rotated weekly instead of using content_focus directly


THEME_CONFIG: list[DayTheme] = [
    DayTheme(
        day="Monday",
        theme_name="Diamond Education",
        content_focus="Teach something valuable about diamonds.",
        needs_product_reference=False,
        rubric_realism_check="conditional",
        content_angles=[
            (
                "Focus on Santrea's unbiased natural-vs-lab-grown diamond "
                "guidance -- help customers understand the real differences "
                "and how to choose without bias."
            ),
            "Explain the 4Cs (cut, color, clarity, carat) in simple, practical terms.",
            "Share a practical diamond care or maintenance tip.",
            "Explain how diamond certification works and why it matters when buying.",
            "Bust a common myth or misconception people have about diamonds.",
            "Explain how diamond setting/mount style affects everyday wearability.",
        ],
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