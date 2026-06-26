"""
Extracts product photos from the image-based catalogue PDF so they can be
used as reference images for gpt-image-1's /images/edits endpoint.

images.edit requires PNG/JPG input under 50MB -- this module converts each
relevant PDF page/image into a clean PNG in assets/catalogue_extracted/.
"""

from pathlib import Path

import fitz  # PyMuPDF

DEFAULT_PDF_PATH = Path("assets/catalogue.pdf")
DEFAULT_OUTPUT_DIR = Path("assets/catalogue_extracted")


def extract_catalogue_images(
    pdf_path: Path = DEFAULT_PDF_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> list[Path]:
    """
    Extract embedded images from each page of the catalogue PDF and save
    them as individual PNG files. Returns the list of saved file paths.

    TODO: once the catalogue is in hand, verify image extraction quality --
    some PDFs embed product photos as one image per page (easy), others
    composite multiple images per page (needs per-image extraction, which
    PyMuPDF's page.get_images() handles -- see commented branch below).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Catalogue PDF not found at {pdf_path}.")

    saved_paths: list[Path] = []
    doc = fitz.open(pdf_path)
    for page_index, page in enumerate(doc):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            out_path = output_dir / f"page{page_index}_img{img_index}.{ext}"
            out_path.write_bytes(image_bytes)
            saved_paths.append(out_path)
    doc.close()
    return saved_paths


def pick_reference_images_for_theme(theme_name: str, max_images: int = 3) -> list[Path]:
    """
    Pick relevant catalogue reference images for a given theme.

    TODO: replace this naive "first N images" placeholder with real selection
    logic once the catalogue has metadata (category, style) to filter on --
    e.g. picking rings for one theme vs. necklaces for another.
    """
    available = sorted(DEFAULT_OUTPUT_DIR.glob("*.png")) + sorted(
        DEFAULT_OUTPUT_DIR.glob("*.jpg")
    )
    return available[:max_images]
