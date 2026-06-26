# Santrea Brand Guidelines

Condensed from the full 40-page visual identity guide (2026). This version keeps the sections that matter for AI content generation -- colors, typography, logo rules, and photography style -- and drops layout/packaging mockup pages that don't affect image prompts.

## Brand essence

Santrea's identity is modern luxury, warmth, and timeless elegance. The palette and photography style should always read as sophisticated, personal, and globally refined -- never loud, never cluttered.

## Brand colors

| Color | Role | Hex | CMYK | RGB |
|---|---|---|---|---|
| Deep Plum | Primary | `#330231` | 72, 91, 46, 63 | 51, 2, 49 |
| Warm Beige | Primary | `#E8D6C4` | 8, 14, 21, 0 | 232, 214, 196 |
| Ivory | Secondary | `#F8F4EE` | 2, 2, 5, 0 | 248, 244, 238 |
| Gold (gradient) | Accent | `#E8C36B` → `#FFFBCE` → `#E8C36B` | -- | -- |

**Usage rules:**
- **Deep Plum** -- primary brand applications: logo, key brand moments, headings, packaging surfaces, premium communication materials.
- **Warm Beige** -- backgrounds, large color areas, supporting brand applications for warmth and softness.
- **Ivory** -- clean negative space, typography support, layouts needing clarity and minimalism.
- **Gold** -- accent only, applied as a gradient (Champagne Gold `#E8C36B` → Light Gold `#FFFBCE` → Champagne Gold `#E8C36B`), for premium finishes such as foil stamping, debossing, embossing, and selected packaging details. Not a primary surface color, and not a flat fill.
- Do not introduce any color outside this approved palette, under any circumstances.

## Typography

| Typeface | Role |
|---|---|
| GC Begia Demo | Display typeface -- large headings only. Sparing use; never for long sentences or dense text. |
| Golden | Sub-headings, labels, titles -- functional counterpart to the display font. |
| Proxima Nova | Body copy -- paragraphs, descriptions, general info. Weights: Light, Regular, Medium, Semi-Bold. |

Hierarchy must stay consistent: GC Begia Demo for headings, Golden for subheads/labels, Proxima Nova for body text. Tracking and leading must follow the brand's defined spacing values -- incorrect spacing reads as unrefined and undermines the premium feel.

## Logo usage

Santrea has four logo forms, each with a defined use case:

- **Primary Logo** (vertical lockup, symbol + wordmark) -- preferred default. Best for vertical/square formats: social posts, vertical banners, product tags, packaging side panels, app splash screens.
- **Secondary Logo** (horizontal lockup) -- for wide formats: website headers, letterheads, business cards, presentation footers, wide banners.
- **Logo Mark** (symbol only) -- for constrained spaces or subtle branding: social avatars, favicons, product engravings, watermarks.
- **Wordmark** (text only) -- for minimal/extreme horizontal or small-scale applications where the symbol would be illegible.

**Logo don'ts (strict, applies to all logo forms):**
- Do not skew or stretch
- Do not outline
- Do not add a drop shadow
- Do not rotate
- Do not add a gradient
- Do not remove the sparkle element
- Do not place any element over the logo
- Do not bold
- Do not join logo paths
- Only use logos in the approved color variations -- no off-palette logo colors

**Clear space:** every logo form requires protective clear space around it (measured from the sparkle element for the mark/primary/secondary logos, or the height of the capital "S" for the wordmark). Nothing -- text, graphics, or page edges -- should crowd this buffer.

**Minimum sizes (digital):** Primary 35px, Secondary 60px, Logo Mark 25px, Wordmark 20px. Below these sizes, fine detail is lost and the logo should not be used.

## Photography style

Santrea's photography is refined and luxurious: clean light, sophisticated composition, modern elegance. Photography carries as much brand weight as the logo -- it should never look casual, cluttered, or harshly lit. When the logo overlays a photo, the underlying area must be clear and high-contrast enough for the logo to stay fully legible -- never placed over a busy or low-contrast region.

## What this means for generated content

For the content agent specifically, every generated image should:
- Use only the approved color palette above (Deep Plum, Warm Beige, Ivory, Gold accents) -- no off-palette colors introduced for "variety". Where gold appears, render it as the light-to-dark gold gradient described above, not a flat gold fill
- Reflect clean, well-lit, uncluttered composition consistent with the brand photography style
- If a logo is rendered, keep it close to the approved forms/colors and avoid the explicit don'ts above (no skew, outline, shadow, rotation, gradient, or missing sparkle) -- minor imperfection is acceptable per the project's quality rubric, but these specific violations should still be avoided
- If typography appears in-image, follow the GC Begia Demo (headings) / Golden (labels) / Proxima Nova (body) hierarchy rather than a generic font
