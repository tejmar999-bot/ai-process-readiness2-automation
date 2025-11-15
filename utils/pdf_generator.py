# utils/pdf_generator.py
from io import BytesIO
from typing import Any, Dict, List, Optional
import os
import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader


# T-Logic color palette (confirmed)
PALETTE = {
    "primary_orange": "#FF6A00",
    "teal": "#12D4C7",
    "red": "#D62839",
    "orange": "#F77F00",
    "amber": "#FBB13C",
    "green": "#2ECC71",
    "blue": "#4C7EFF",
    "purple": "#A066FF",
    "bg": "#121519",
    "text": "#111111",
}

BAR_COLORS = [
    PALETTE["red"],
    PALETTE["orange"],
    PALETTE["amber"],
    PALETTE["green"],
    PALETTE["blue"],
    PALETTE["purple"],
]


def _wrap_text(text: str, max_width: float, fontname: str, fontsize: int) -> List[str]:
    """Wrap text to fit target width using font metrics."""
    if not text:
        return []
    words = text.split()
    lines: List[str] = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        # stringWidth returns float; compare to float width
        if stringWidth(test, fontname, fontsize) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def _hex_to_rgb(hexcolor: str) -> tuple:
    """Convert #RRGGBB to (r,g,b) 0-1 floats for reportlab setFillColorRGB"""
    hexcolor = hexcolor.lstrip("#")
    r = int(hexcolor[0:2], 16) / 255.0
    g = int(hexcolor[2:4], 16) / 255.0
    b = int(hexcolor[4:6], 16) / 255.0
    return (r, g, b)


def generate_pdf_report(
    results: Dict[str, Any],
    company_name: Optional[str] = None,
    primary_color: str = PALETTE["primary_orange"],
    logo_path: Optional[str] = None,
    include_bars: bool = True,
) -> bytes:
    """
    Generate a branded PDF report using ReportLab and return bytes.

    results: Dict should include:
        - total: numeric (0-30)
        - percentage: numeric (0-100)
        - readiness_band: dict with 'label' and optional 'description'
        - dimension_scores: list of dicts or numbers (each dimension)
            when dict: { "title": str, "description": str, "score": float }
        - notes: optional text
        - recommendations: optional list[str]
    """

    # Create buffer
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Layout constants
    left_margin = 18 * mm
    right_margin = 18 * mm
    usable_width = width - left_margin - right_margin
    top = height - 18 * mm
    y = top

    # Draw header rectangle (thin band) with primary color
    band_height = 18 * mm
    r, g, b = _hex_to_rgb(primary_color)
    c.setFillColorRGB(r, g, b)
    c.rect(0, height - band_height, width, band_height, stroke=0, fill=1)

    # Place logo on the left within the band if provided
    logo_drawn = False
    if logo_path and os.path.isfile(logo_path):
        try:
            logo = ImageReader(logo_path)
            # scale logo to band height (with padding)
            padding = 3 * mm
            logo_max_h = band_height - 2 * padding
            # compute width preserving aspect ratio
            iw, ih = logo.getSize()
            scale = logo_max_h / float(ih)
            logo_w = iw * scale
            logo_h = logo_max_h
            c.drawImage(logo, left_margin, height - padding - logo_h, width=logo_w, height=logo_h, mask="auto")
            logo_drawn = True
            logo_x_end = left_margin + logo_w + 6 * mm
        except Exception:
            logo_drawn = False

    # Title text on the band (if logo present, start after logo)
    title_x = left_margin if not logo_drawn else (logo_x_end)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 14)
    header_title = company_name + " — AI-Enabled Process Readiness" if company_name else "AI-Enabled Process Readiness"
    c.drawString(title_x, height - band_height + 4 * mm, header_title)

    y = height - band_height - 10 * mm

    # Small subtitle
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    subtitle = results.get("subtitle", "Free 3-minute operational readiness assessment")
    sublines = _wrap_text(subtitle, usable_width * 0.7, "Helvetica", 10)
    for line in sublines:
        c.drawString(left_margin, y, line)
        y -= 6 * mm
    y -= 2 * mm

    # Overall score box
    total = results.get("total", 0)
    percentage = results.get("percentage", 0)
    readiness_band = results.get("readiness_band", {})
    band_label = readiness_band.get("label", "N/A")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, f"Overall Score: {total:.1f} / 30    ({percentage}%)")
    y -= 7 * mm
    c.setFont("Helvetica", 10)
    c.drawString(left_margin, y, f"Readiness Level: {band_label}")
    y -= 10 * mm

    # Draw dimension bars summary (rainbow) if requested
    dims = results.get("dimension_scores", [])
    if include_bars and dims:
        bar_h = 7 * mm
        gap = 4 * mm
        # Draw up to 6 bars in palette order; use score to set fill width
        for idx, color in enumerate(BAR_COLORS[: len(dims)]):
            # compute bar background rectangle position
            bar_y = y - (idx * (bar_h + gap))
            bar_x = left_margin
            bar_w = usable_width * 0.55  # summary bar width
            # background light rect
            c.setFillColorRGB(0.9, 0.9, 0.9)
            c.roundRect(bar_x, bar_y, bar_w, bar_h, 2 * mm, stroke=0, fill=1)
            # filled width from score (if numeric)
            score_value = 0.0
            entry = dims[idx]
            if isinstance(entry, dict):
                score_value = float(entry.get("score", 0) if entry.get("score", 0) is not None else 0)
            else:
                try:
                    score_value = float(entry)
                except Exception:
                    score_value = 0.0
            fill_pct = max(0.0, min(1.0, score_value / 5.0))
            fill_w = bar_w * fill_pct
            r, g, b = _hex_to_rgb(color)
            c.setFillColorRGB(r, g, b)
            c.roundRect(bar_x, bar_y, fill_w, bar_h, 2 * mm, stroke=0, fill=1)
        # move y below the bars
        y = y - (len(dims) * (bar_h + gap)) - 6 * mm

    # Dimension breakdown details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Dimension Breakdown:")
    y -= 8 * mm

    # For each dimension: title, score bar, description
    dims_to_iterate = dims if isinstance(dims, list) else []
    for i, entry in enumerate(dims_to_iterate):
        if y < 40 * mm:
            c.showPage()
            y = top - band_height

        if isinstance(entry, dict):
            title = entry.get("title", f"Dimension {i+1}")
            desc = entry.get("description", "")
            score = float(entry.get("score", 0) if entry.get("score", 0) is not None else 0)
        else:
            title = f"Dimension {i+1}"
            desc = ""
            try:
                score = float(entry)
            except Exception:
                score = 0.0

        # Title and numeric
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_margin, y, f"{i+1}. {title}")
        c.setFont("Helvetica", 10)
        c.drawRightString(left_margin + usable_width, y, f"{score:.1f} / 5")
        y -= 6 * mm

        # Score bar (visual)
        bar_total_w = usable_width * 0.7
        bar_h = 6 * mm
        bar_x = left_margin
        bar_y = y - bar_h
        # background
        c.setFillColorRGB(0.92, 0.92, 0.92)
        c.roundRect(bar_x, bar_y, bar_total_w, bar_h, 1.5 * mm, stroke=0, fill=1)
        # fill color for this dimension (loop palette)
        color = BAR_COLORS[i % len(BAR_COLORS)]
        r, g, b = _hex_to_rgb(color)
        c.setFillColorRGB(r, g, b)
        fill_w = bar_total_w * max(0.0, min(1.0, score / 5.0))
        c.roundRect(bar_x, bar_y, fill_w, bar_h, 1.5 * mm, stroke=0, fill=1)
        y = bar_y - 4 * mm

        # Description (wrapped)
        if desc:
            c.setFont("Helvetica", 9)
            wrapped = _wrap_text(desc, usable_width * 0.95, "Helvetica", 9)
            for line in wrapped:
                c.drawString(left_margin + 4 * mm, y, line)
                y -= 5 * mm
            y -= 3 * mm
        else:
            y -= 2 * mm

    # Recommendations section
    recs = results.get("recommendations", [])
    if recs:
        if y < 60 * mm:
            c.showPage()
            y = top - band_height
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, "Key Recommendations:")
        y -= 8 * mm
        c.setFont("Helvetica", 10)
        for rtext in recs:
            wrapped = _wrap_text(rtext, usable_width * 0.95, "Helvetica", 10)
            for line in wrapped:
                c.drawString(left_margin + 4 * mm, y, f"• {line}" if line == wrapped[0] else f"  {line}")
                y -= 5 * mm
            y -= 4 * mm

    # Notes
    notes = results.get("notes", "")
    if notes:
        if y < 60 * mm:
            c.showPage()
            y = top - band_height
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, "Notes:")
        y -= 8 * mm
        c.setFont("Helvetica", 10)
        wrapped = _wrap_text(notes, usable_width * 0.95, "Helvetica", 10)
        for line in wrapped:
            c.drawString(left_margin + 4 * mm, y, line)
            y -= 5 * mm

    # Footer (small)
    if y < 40 * mm:
        c.showPage()
        y = top - band_height
    c.setFont("Helvetica", 8)
    footer_text = "T-Logic Consulting • AI-Enabled Process Readiness • Confidential"
    c.drawString(left_margin, 12 * mm, footer_text)
    # small print on right
    c.drawRightString(width - right_margin, 12 * mm, f"Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
