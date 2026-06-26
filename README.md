# Santre Content Agent

An automated weekly content pipeline for the Santre jewellery brand. Generates
on-brand social media images and captions for 3 days a week (Monday, Tuesday,
Saturday), with an automated AI quality-review and retry loop, and writes
output to Google Drive + Google Sheets.

## Status

This is the initial scaffold -- module structure and stub logic are in place,
but real run-throughs and prompt tuning are still needed. See TODOs in each
module.

## Setup

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in:
   - `OPENAI_API_KEY`
   - `GOOGLE_SERVICE_ACCOUNT_JSON` (path to a Google service account key file)
   - `GOOGLE_DRIVE_PARENT_FOLDER_ID` (Drive folder shared with the service account)
   - `GOOGLE_SHEETS_SPREADSHEET_ID` (Sheet shared with the service account)
3. Add your context documents:
   - `assets/brand_guidelines.md`
   - `assets/brand_positioning.md`
   - `assets/catalogue.pdf`
4. Run catalogue extraction once: `python -c "from src.context.catalogue import extract_catalogue_images; extract_catalogue_images()"`
5. Run the pipeline manually: `python -m src.orchestrator`

## Scheduling

`.github/workflows/weekly_run.yml` runs this automatically every Sunday via
GitHub Actions cron. Add the same secrets (`OPENAI_API_KEY`,
`GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_DRIVE_PARENT_FOLDER_ID`,
`GOOGLE_SHEETS_SPREADSHEET_ID`) under the repo's Settings -> Secrets and
variables -> Actions.

## Architecture

See the foundation document for full design decisions (rubric, retry logic,
scope, stack rationale).

## Project structure

```
src/
  config/       day -> theme configuration
  context/      loaders for brand guidelines, positioning, catalogue
  generation/   prompt building, image generation, caption generation
  review/       automated vision-based quality scoring
  output/       Drive upload, Sheets writing
  orchestrator.py   ties it all together, entry point for the cron job
```
