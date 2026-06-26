# Santre Content Agent

An automated weekly content pipeline that generates on-brand social media images and captions for a jewellery brand. Runs on a GitHub Actions cron every Sunday, producing content for three days of the week (Monday, Tuesday, Saturday), and writes the output to Google Drive and Google Sheets.

Each run:
1. Generates images using OpenAI's image model, grounded in your brand guidelines
2. Scores each image with a vision model against a quality rubric; retries on failure (up to 3 attempts)
3. Composites your real logo onto approved images
4. Generates a WhatsApp caption or poll to accompany the image
5. Uploads everything to Google Drive and logs it in a Google Sheet

---

## Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys) with access to `gpt-image-2` and `gpt-4o`
- A Google account to receive output (Drive + Sheets)
- A GitHub repository to host and run the automation

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in the values:

| Variable | What it is |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Path to your Google service account JSON file (e.g. `service_account.json`) |
| `GOOGLE_DRIVE_PARENT_FOLDER_ID` | ID of the Drive folder where weekly image folders will be created |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | ID of the Google Sheet where weekly output tabs will be created |

> The folder/sheet IDs are the long alphanumeric strings in the URL when you open Drive or Sheets:
> `https://drive.google.com/drive/folders/THIS_PART`
> `https://docs.google.com/spreadsheets/d/THIS_PART`

### 3. Set up Google Drive access

The pipeline authenticates to Google Drive using OAuth (your personal Google account), not a service account. This lets the files appear in your own Drive rather than a service account's drive.

**One-time setup:**

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a project
2. Enable the **Google Drive API** and **Google Sheets API** for the project
3. Under **APIs & Services → Credentials**, create an **OAuth 2.0 Client ID** (Desktop app type)
4. Download the JSON and save it as `client_secret.json` in the project root
5. Run the token generator once to authenticate:

```bash
python scripts/generate_drive_token.py
```

This opens a browser window, you log in with your Google account, and a `token.json` is saved. The pipeline uses this token for all future runs (it auto-refreshes).

> `client_secret.json` and `token.json` are already in `.gitignore`. Do not commit them.

### 4. Share your Drive folder and Sheet with the pipeline

Open your target Google Drive folder and Google Sheet, and share both with the Google account that owns the `token.json` you generated (i.e., yourself), with at least **Editor** access.

### 5. Add your brand assets

Place the following files in the `assets/` directory:

| File | Purpose |
|---|---|
| `assets/brand_guidelines.md` | Visual identity: colors, typography, photography style, logo rules |
| `assets/brand_positioning.md` | Voice and messaging: audience, tone, differentiators, caption guidance |
| `assets/catalogue/` | Product reference images (PNG or JPG). Used on product showcase days |
| `assets/logo/` | Logo files used for compositing (see [Customising the logo](#customising-the-logo)) |

### 6. Run the catalogue extractor

If you have a product catalogue PDF, extract its images once before running the pipeline:

```bash
python -c "from src.context.catalogue import extract_catalogue_images; extract_catalogue_images()"
```

Otherwise, put product images directly into `assets/catalogue/` as PNG or JPG files.

### 7. Run the pipeline manually

```bash
python -m src.orchestrator
```

This runs one full weekly cycle immediately. Check your Drive folder and Google Sheet for output.

---

## GitHub Actions automation

The pipeline runs automatically every Sunday at 9:00 AM IST via `.github/workflows/weekly_run.yml`.

### Add secrets to your repo

Go to **Settings → Secrets and variables → Actions** and add:

| Secret name | Value |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | The full JSON content of your `service_account.json` (paste the whole thing) |
| `GOOGLE_DRIVE_PARENT_FOLDER_ID` | Drive folder ID |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | Google Sheet ID |

> The workflow writes this JSON to a file at runtime and passes its path to the pipeline.

### Manual trigger

You can trigger a run any time from **Actions → Weekly content generation → Run workflow** without waiting for Sunday.

---

## Customising for your brand

Everything brand-specific lives in a handful of files. You do not need to touch the pipeline code to adapt this to a different brand.

### Brand voice and visuals

**`assets/brand_guidelines.md`** — paste your visual identity guidance here. The image generation prompt injects this verbatim. Include:
- Color palette (hex values help)
- Typography rules
- Photography style
- Logo usage rules and placement guidance

**`assets/brand_positioning.md`** — paste your voice and messaging context here. The caption/poll generation prompt injects this verbatim. Include:
- Brand name, tagline
- Target audience
- Tone and personality
- What makes you different from competitors
- What the generated text should and should not do

The more specific these files are, the better the output will be. Vague guidelines produce generic content.

### Content schedule and themes

**`src/config/themes.py`** — defines which days get content and what the theme is for each day. Each entry is a `DayTheme`:

```python
DayTheme(
    day="Monday",                          # Label used in Drive/Sheets output
    theme_name="Diamond Education",        # Short name for the theme
    content_focus="Teach something ...",   # What the image + caption should focus on
    needs_product_reference=False,         # True = pull a catalogue image as visual reference
    rubric_realism_check="conditional",    # "always" | "conditional" | "never"
    output_format="message",               # "message" (caption) or "poll" (WhatsApp poll)
    content_angles=[                       # Optional: rotate through these angles weekly
        "Angle A ...",
        "Angle B ...",
    ],
)
```

To change the posting days, edit or replace the three entries in `THEME_CONFIG`. To post 7 days a week, add four more entries.

`content_angles` is useful when a theme recurs weekly — the pipeline cycles through the angles by ISO week number so the same sub-topic does not repeat every week.

### Customising the logo

The pipeline composites your logo onto approved images automatically. It picks between two shapes (logomark vs monogram) based on the image composition, and picks between dark/light/gold versions based on the brightness of the area the logo will land on.

Prepare your logo files and place them in `assets/logo/`:

| Filename | When used |
|---|---|
| `logomark_dark.png` | Compact symbol, dark variant (for light backgrounds) |
| `logomark_light.png` | Compact symbol, light variant (for dark backgrounds) |
| `logomark_gold.png` | Compact symbol, gold variant (manual override only) |
| `monogram_dark.png` | Lettering/initial mark, dark variant |
| `monogram_light.png` | Lettering/initial mark, light variant |
| `monogram_gold.png` | Lettering/initial mark, gold variant |

All files should be PNG with a transparent background. If your brand only has one logo shape, use the same file for both `logomark_*` and `monogram_*` variants.

Logo placement defaults to `bottom-right`. To change placement or size, edit the `composite_logo` call in `src/orchestrator.py`:

```python
image_bytes = composite_logo(
    image_bytes,
    position="bottom-left",   # "bottom-right" | "bottom-left" | "top-right" | "top-left"
    logo_width_ratio=0.12,    # logo width as a fraction of image width
    margin_ratio=0.04,        # margin from edge as a fraction of image width
)
```

### Adjusting image quality and retry budget

In `src/orchestrator.py`:

```python
MAX_RETRIES = 3        # how many image generation attempts before giving up
IMAGE_QUALITY = "high" # "low" | "medium" | "high" — lower = faster and cheaper
```

`"high"` quality produces the best images but costs more. Use `"medium"` while tuning prompts, then switch to `"high"` for production.

---

## Project structure

```
assets/
  brand_guidelines.md    visual identity fed into image prompts
  brand_positioning.md   voice/messaging fed into caption prompts
  catalogue/             product reference images
  logo/                  logo variants for compositing

scripts/
  generate_drive_token.py  one-time OAuth token setup for Google Drive

src/
  config/
    themes.py            day → theme configuration
  context/
    brand_guidelines.py  loads brand_guidelines.md
    brand_positioning.py loads brand_positioning.md
    catalogue.py         loads/picks product reference images
  generation/
    prompt_builder.py    builds image, caption, and poll prompts
    image_generator.py   calls OpenAI image generation API
    caption_generator.py calls OpenAI text API for captions and polls
    logo_compositor.py   composites logo onto generated images
  review/
    scorer.py            vision-model quality scoring and poll alignment check
  output/
    drive_uploader.py    uploads images to Google Drive
    sheets_writer.py     logs output rows to Google Sheets
  orchestrator.py        entry point — ties everything together

.github/workflows/
  weekly_run.yml         GitHub Actions cron (Sundays, 9am IST)
```

---

## Output format

For each day, the pipeline writes one row to a Google Sheet tab named `Week_YYYY-MM-DD`:

| Day | Theme | Image link | Caption / Poll | Status | Retry count |
|---|---|---|---|---|---|
| Monday | Diamond Education | Drive link | Caption text | Approved | 1 |
| Tuesday | Jewellery Inspiration | Drive link | Caption text | Approved | 2 |
| Saturday | Engagement | Drive link | Poll text | Approved | 1 |

Images land in a Drive folder at `{parent folder} / Week_YYYY-MM-DD / {day}.png`.

**Status values:**
- `Approved` — passed the vision quality check
- `Flagged` — failed all retries; image is still uploaded for manual review
- `Approved (poll flagged for manual check)` — image approved but poll text did not pass alignment check
