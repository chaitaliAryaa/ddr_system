"""
extractor.py
Extracts text and images from PDF documents using PyMuPDF.
"""

import fitz  # PyMuPDF
import os
import base64
from PIL import Image
import io


def extract_from_pdf(pdf_path: str, output_images_dir: str = "extracted_images") -> dict:
    """
    Extract all text and images from a PDF file.

    Args:
        pdf_path: Path to the PDF file.
        output_images_dir: Directory to save extracted images.

    Returns:
        dict with keys:
            - 'text': full text string
            - 'pages': list of dicts per page (page_num, text, images)
            - 'images': list of dicts (page_num, image_path, base64)
    """
    os.makedirs(output_images_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    full_text = []
    pages_data = []
    all_images = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # --- Extract text ---
        page_text = page.get_text("text")
        full_text.append(f"\n--- Page {page_num + 1} ---\n{page_text}")

        # --- Extract images ---
        page_images = []
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Skip tiny images (likely icons/decorations)
                pil_img = Image.open(io.BytesIO(image_bytes))
                w, h = pil_img.size
                if w < 50 or h < 50:
                    continue

                # Save image to disk
                img_filename = f"page{page_num+1}_img{img_index+1}.{image_ext}"
                img_path = os.path.join(output_images_dir, img_filename)
                with open(img_path, "wb") as f:
                    f.write(image_bytes)

                # Convert to base64 for API
                b64 = base64.b64encode(image_bytes).decode("utf-8")

                img_data = {
                    "page_num": page_num + 1,
                    "image_path": img_path,
                    "base64": b64,
                    "ext": image_ext,
                    "filename": img_filename,
                    "size": (w, h),
                }
                page_images.append(img_data)
                all_images.append(img_data)

            except Exception as e:
                print(f"[extractor] Skipped image on page {page_num+1}: {e}")

        pages_data.append(
            {
                "page_num": page_num + 1,
                "text": page_text,
                "images": page_images,
            }
        )

    doc.close()

    return {
        "text": "\n".join(full_text),
        "pages": pages_data,
        "images": all_images,
    }


def get_image_media_type(ext: str) -> str:
    """Return MIME type for image extension."""
    mapping = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    return mapping.get(ext.lower(), "image/jpeg")
