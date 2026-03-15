"""
report_builder.py
Converts the DDR markdown text into a professional Word document (.docx)
with images embedded in the appropriate sections.
"""

import os
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime
from PIL import Image
import io


# ── Helpers ──────────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color: str):
    """Set table cell background color."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_horizontal_rule(doc):
    """Add a thin horizontal line."""
    para = doc.add_paragraph()
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "CCCCCC")
    pBdr.append(bottom)
    pPr.append(pBdr)
    return para


def severity_color(severity_text: str) -> str:
    """Map severity level to hex color."""
    s = severity_text.upper().strip()
    if "CRITICAL" in s:
        return "FF4444"
    elif "HIGH" in s:
        return "FF8C00"
    elif "MEDIUM" in s:
        return "FFD700"
    elif "LOW" in s:
        return "4CAF50"
    return "FFFFFF"


# ── Image resolution ─────────────────────────────────────────────────────────

def find_image_path(filename: str, inspection_images: list, thermal_images: list) -> str | None:
    """Find image file path by filename."""
    all_images = inspection_images + thermal_images
    for img in all_images:
        if img["filename"] == filename or filename in img["filename"]:
            if os.path.exists(img["image_path"]):
                return img["image_path"]
    return None


def extract_image_references(text: str) -> list:
    """Extract [RELEVANT_IMAGE: filename] tags from DDR text."""
    pattern = r"\[RELEVANT_IMAGE:\s*([^\]]+)\]"
    matches = re.findall(pattern, text)
    return [m.strip() for m in matches if m.strip().lower() not in ("none", "n/a", "")]


# ── Document styling ──────────────────────────────────────────────────────────

def style_document(doc):
    """Apply base styles to document."""
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)


def add_cover_page(doc, property_name: str = "Property Inspection"):
    """Add a professional cover page."""
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("DETAILED DIAGNOSTIC REPORT")
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = RGBColor(0x1A, 0x56, 0x8C)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = subtitle.add_run(property_name)
    run2.font.size = Pt(16)
    run2.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    doc.add_paragraph()
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_run = date_para.add_run(f"Report Date: {datetime.now().strftime('%B %d, %Y')}")
    date_run.font.size = Pt(12)
    date_run.font.color.rgb = RGBColor(0x77, 0x77, 0x77)

    doc.add_page_break()


# ── Section renderers ─────────────────────────────────────────────────────────

def render_section_heading(doc, text: str, level: int = 1):
    """Add a styled section heading."""
    if level == 1:
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x1A, 0x56, 0x8C)
        p.space_before = Pt(16)
        p.space_after = Pt(4)
        add_horizontal_rule(doc)
    elif level == 2:
        p = doc.add_heading(text, level=2)
        p.runs[0].font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)
    return p


def render_table(doc, lines: list):
    """Parse markdown table lines and render as Word table."""
    rows = []
    for line in lines:
        if re.match(r"^\|[-| ]+\|$", line.strip()):
            continue  # separator row
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells:
            rows.append(cells)

    if not rows:
        return

    n_cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.style = "Table Grid"

    for i, row_data in enumerate(rows):
        for j, cell_text in enumerate(row_data):
            if j >= n_cols:
                break
            cell = table.rows[i].cells[j]
            cell.text = cell_text
            if i == 0:
                # Header row
                cell.paragraphs[0].runs[0].bold = True
                set_cell_bg(cell, "1A568C")
                cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                # Color severity cells
                upper = cell_text.upper()
                if upper in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
                    set_cell_bg(cell, severity_color(cell_text))

    doc.add_paragraph()


def insert_image(doc, img_path: str, caption: str = ""):
    """Insert an image with optional caption."""
    try:
        # Resize if too wide
        with Image.open(img_path) as pil_img:
            w, h = pil_img.size
            max_width_inches = 5.5
            dpi = 96
            width_inches = w / dpi
            display_width = min(width_inches, max_width_inches)

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(img_path, width=Inches(display_width))

        if caption:
            cap = doc.add_paragraph(caption)
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.runs[0].italic = True
            cap.runs[0].font.size = Pt(9)
            cap.runs[0].font.color.rgb = RGBColor(0x77, 0x77, 0x77)

    except Exception as e:
        doc.add_paragraph(f"[Image could not be inserted: {e}]")


# ── Main builder ─────────────────────────────────────────────────────────────

def build_docx_report(
    ddr_text: str,
    inspection_images: list,
    thermal_images: list,
    output_path: str = "DDR_Report.docx",
    property_name: str = "Property Inspection",
) -> str:
    """
    Build a Word document from DDR markdown text.

    Args:
        ddr_text: Markdown-formatted DDR from Claude.
        inspection_images: List of image dicts from inspection PDF.
        thermal_images: List of image dicts from thermal PDF.
        output_path: Path to save the .docx file.
        property_name: Title on cover page.

    Returns:
        Path to the saved .docx file.
    """
    doc = Document()
    style_document(doc)
    add_cover_page(doc, property_name)

    all_images = inspection_images + thermal_images
    lines = ddr_text.split("\n")
    i = 0
    in_table = False
    table_lines = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Image reference tag ──────────────────────────────────────
        img_match = re.match(r"\[RELEVANT_IMAGE:\s*([^\]]+)\]", stripped)
        if img_match:
            ref = img_match.group(1).strip()
            if ref.lower() not in ("none", "n/a", ""):
                img_path = find_image_path(ref, inspection_images, thermal_images)
                if img_path:
                    insert_image(doc, img_path, caption=f"Figure: {ref}")
                else:
                    doc.add_paragraph(f"[Image Not Available: {ref}]").runs[0].italic = True
            i += 1
            continue

        # ── Table detection ──────────────────────────────────────────
        if stripped.startswith("|"):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(stripped)
            i += 1
            continue
        else:
            if in_table:
                render_table(doc, table_lines)
                in_table = False
                table_lines = []

        # ── Headings ─────────────────────────────────────────────────
        if stripped.startswith("## "):
            render_section_heading(doc, stripped[3:], level=1)
        elif stripped.startswith("### "):
            render_section_heading(doc, stripped[4:], level=2)
        elif stripped.startswith("# "):
            p = doc.add_heading(stripped[2:], level=1)

        # ── Bullet points ─────────────────────────────────────────────
        elif stripped.startswith("- ") or stripped.startswith("* "):
            p = doc.add_paragraph(stripped[2:], style="List Bullet")
            p.space_after = Pt(2)

        # ── Numbered list ─────────────────────────────────────────────
        elif re.match(r"^\d+\.\s", stripped):
            p = doc.add_paragraph(stripped, style="List Number")
            p.space_after = Pt(2)

        # ── Bold text (inline) ────────────────────────────────────────
        elif "**" in stripped and stripped:
            p = doc.add_paragraph()
            parts = re.split(r"\*\*", stripped)
            for idx, part in enumerate(parts):
                run = p.add_run(part)
                if idx % 2 == 1:
                    run.bold = True

        # ── Empty line ────────────────────────────────────────────────
        elif stripped == "":
            if i > 0 and lines[i - 1].strip() != "":
                doc.add_paragraph()

        # ── Regular paragraph ─────────────────────────────────────────
        else:
            if stripped:
                p = doc.add_paragraph(stripped)
                p.space_after = Pt(4)

        i += 1

    # Flush any remaining table
    if in_table and table_lines:
        render_table(doc, table_lines)

    # ── Footer: embed all extracted images at end ─────────────────────
    if all_images:
        doc.add_page_break()
        render_section_heading(doc, "Appendix: All Extracted Images", level=1)

        for img_data in all_images:
            if os.path.exists(img_data["image_path"]):
                source = "Inspection Report" if img_data in inspection_images else "Thermal Report"
                doc.add_paragraph(
                    f"Source: {source} | Page: {img_data['page_num']} | File: {img_data['filename']}"
                ).runs[0].bold = True
                insert_image(doc, img_data["image_path"], caption=img_data["filename"])
                doc.add_paragraph()

    doc.save(output_path)
    return output_path
