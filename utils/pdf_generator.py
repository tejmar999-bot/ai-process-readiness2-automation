# utils/pdf_generator.py
"""
ReportLab PDF generator — T-Logic "Signature Blueprint" style (dark theme).
Produces a single- or multi-page PDF and returns raw bytes suitable for
streamlit.download_button(..., data=pdf_bytes, ...)

Uses:
 - attached_assets/TLogic_Logo6.png as default logo (if present)
 - No external dependencies beyond reportlab
"""

from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple
import os
import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader


# Palette (confirmed)
PALETTE = {
    "primary_orange": "#FF6A00",
    "teal": "#12D4C7",
    "red": "#D62839",
    "orange": "#F77F00",
    "amber": "#FBB13C",
    "green": "#2ECC71",
    "blue": "#4C7EFF",
    "purple": "#A066FF",
    "bg_dark": "#0F1214",   # deep almost-black page background
    "panel_dark": "#16191B", # slightly lighter panel color
    "muted_text": "#CBCFD1",
    "white": "#FFFFFF",
}

BAR_COLORS = [
    PALETTE["red"],
    PALETTE["orange"],
    PALETTE["amber"],
    PALETTE["green"],
    PALETTE["blue"],
    PALETTE["purple"],
]


def _hex_to_rgb(hexcolor: str) -> Tuple[float, float, float]:
    s = hexcolor.lstrip("#")
    return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0, int(s[4:6], 16) / 255.0)


def _wrap_text(text: str, max_width: float, fontname: str, fontsize: int) -> List[str]:
    if not text:
        return []
    words = text.split()
    lines: List[str] = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        if stringWidth(test, fontname, fontsize) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def generate_pdf_report(
    results: Dict[str, Any],
    company_name: Optional[str] = None,
    tagline: Optional[str] = "AI-Enabled Readiness Assessment",
    logo_path: Optional[str] = "attached_assets/TLogic_Logo6.png",
    primary_color: str = PALETTE["primary_orange"],
    include_bars: bool = True,
) -> bytes:
    """
    Generate a dark-theme, branded PDF and return bytes.

    results keys (recommended):
      - total: number
      - percentage: number (0-100)
      - readiness_band: {label: str, description: str}
      - dimension_scores: list of dict or numbers
          dict => {"title": str, "description": str, "score": float}
      - notes: str
      - recommendations: list[str]
      - subtitle: optional str
    """

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Page background (dark)
    r, g, b = _hex_to_rgb(PALETTE["bg_dark"])
    c.setFillColorRGB(r, g, b)
    c.rect(0, 0, width, height, stroke=0, fill=1)

    # Layout
    left = 18 * mm
    right = 18 * mm
    usable_w = width - left - right
    top = height - 18 * mm
    y = top

    # Header band
    band_h = 22 * mm
    r, g, b = _hex_to_rgb(primary_color)
    c.setFillColorRGB(r, g, b)
    c.rect(0, height - band_h, width, band_h, stroke=0, fill=1)

    # Logo (left) inside band if exists
    logo_drawn = False
    if logo_path and os.path.isfile(logo_path):
        try:
            img = ImageReader(logo_path)
            iw, ih = img.getSize()
            # scale to band height minus padding
            padding = 3 * mm
            target_h = band_h - (2 * padding)
            scale = target_h / float(ih)
            logo_w = iw * scale
            logo_h = target_h
            logo_x = left
            logo_y = height - padding - logo_h
            c.drawImage(img, logo_x, logo_y, width=logo_w, height=logo_h, mask="auto")
            logo_drawn = True
            text_x = logo_x + logo_w + 8 * mm
        except Exception:
            logo_drawn = False
            text_x = left
    else:
        text_x = left

    # Header text (white)
    c.setFillColorRGB(*_hex_to_rgb(PALETTE["white"]))
    c.setFont("Helvetica-Bold", 14)
    header_title = f"{company_name} — AI-Enabled Process Readiness" if company_name else "AI-Enabled Process Readiness"
    c.drawString(text_x, height - band_h + 6 * mm, header_title)

    # Tagline small (if provided)
    if tagline:
        c.setFont("Helvetica", 9)
        c.drawString(text_x, height - band_h + 2 * mm, tagline)

    # Move under header
    y = height - band_h - 8 * mm

    # Subtitle (lighter)
    subtitle = results.get("subtitle", "")
    if subtitle:
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(*_hex_to_rgb(PALETTE["muted_text"]))
        wrapped = _wrap_text(subtitle, usable_w * 0.85, "Helvetica", 10)
        for line in wrapped:
            c.drawString(left, y, line)
            y -= 6 * mm
        y -= 4 * mm

    # Overall score & band
    total = results.get("total", 0)
    percentage = results.get("percentage", 0)
    band = results.get("readiness_band", {})
    band_label = band.get("label", "")

    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(*_hex_to_rgb(PALETTE["white"]))
    c.drawString(left, y, f"Overall Score: {total:.1f} / 30  ({percentage}%)")
    y -= 7 * mm
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(*_hex_to_rgb(PALETTE["muted_text"]))
    c.drawString(left, y, f"Readiness Level: {band_label}")
    y -= 10 * mm

    # Rainbow bars summary (left column)
    dims = results.get("dimension_scores", [])
    if include_bars and isinstance(dims, list) and len(dims) > 0:
        bar_h = 7 * mm
        gap = 5 * mm
        max_bars = min(6, len(dims))
        for i in range(max_bars):
            entry = dims[i]
            score = 0.0
            if isinstance(entry, dict):
                score = float(entry.get("score", 0) or 0)
            else:
                try:
                    score = float(entry)
                except Exception:
                    score = 0.0
            # background
            bar_x = left
            bar_w = usable_w * 0.6
            bar_y = y - i * (bar_h + gap)
            c.setFillColorRGB(0.16, 0.17, 0.18)  # muted dark background for bar
            c.roundRect(bar_x, bar_y, bar_w, bar_h, 1.8 * mm, stroke=0, fill=1)
            # fill
            fill_pct = max(0.0, min(1.0, score / 5.0))
            fill_w = bar_w * fill_pct
            r, g, b = _hex_to_rgb(BAR_COLORS[i % len(BAR_COLORS)])
            c.setFillColorRGB(r, g, b)
            c.roundRect(bar_x, bar_y, fill_w, bar_h, 1.8 * mm, stroke=0, fill=1)
        y = y - (max_bars * (bar_h + gap)) - 8 * mm

    # Dimension breakdown: full details (each dimension)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(*_hex_to_rgb(PALETTE["white"]))
    c.drawString(left, y, "Dimension Breakdown")
    y -= 8 * mm

    for i, entry in enumerate(dims):
        if y < 40 * mm:
            c.showPage()
            # redraw background & header band on new page
            c.setFillColorRGB(*_hex_to_rgb(PALETTE["bg_dark"]))
            c.rect(0, 0, width, height, stroke=0, fill=1)
            # small header on subsequent pages
            c.setFillColorRGB(*_hex_to_rgb(primary_color))
            c.rect(0, height - band_h, width, band_h, stroke=0, fill=1)
            c.setFillColorRGB(*_hex_to_rgb(PALETTE["white"]))
            c.setFont("Helvetica-Bold", 13)
            c.drawString(left, height - band_h + 6 * mm, header_title)
            y = height - band_h - 10 * mm

        if isinstance(entry, dict):
            title = entry.get("title", f"Dimension {i+1}")
            desc = entry.get("description", "")
            score = float(entry.get("score", 0) or 0)
        else:
            title = f"Dimension {i+1}"
            desc = ""
            try:
                score = float(entry)
            except Exception:
                score = 0.0

        # Title + numeric
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(*_hex_to_rgb(PALETTE["white"]))
        c.drawString(left, y, f"{i+1}. {title}")
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(*_hex_to_rgb(PALETTE["muted_text"]))
        c.drawRightString(left + usable_w, y, f"{score:.1f} / 5")
        y -= 6 * mm

        # visual bar
        bar_total_w = usable_w * 0.65
        bar_h = 6 * mm
        bar_x = left
        bar_y = y - bar_h
        c.setFillColorRGB(0.16, 0.17, 0.18)
        c.roundRect(bar_x, bar_y, bar_total_w, bar_h, 1.6 * mm, stroke=0, fill=1)
        r, g, b = _hex_to_rgb(BAR_COLORS[i % len(BAR_COLORS)])
        c.setFillColorRGB(r, g, b)
        c.roundRect(bar_x, bar_y, bar_total_w * max(0.0, min(1.0, score / 5.0)), bar_h, 1.6 * mm, stroke=0, fill=1)
        y = bar_y - 5 * mm

        # description
        if desc:
            c.setFont("Helvetica", 9)
            c.setFillColorRGB(*_hex_to_rgb(PALETTE["muted_text"]))
            wrapped = _wrap_text(desc, usable_w * 0.95, "Helvetica", 9)
            for ln in wrapped:
                c.drawString(left + 3 * mm, y, ln)
                y -= 5 * mm
            y -= 4 * mm

    # Recommendations
    recs = results.get("recommendations", []) or []
    if recs:
        if y < 80 * mm:
            c.showPage()
            c.setFillColorRGB(*_hex_to_rgb(PALETTE["bg_dark"]))
            c.rect(0, 0, width, height, stroke=0, fill=1)
            y = height - band_h - 10 * mm
        c.setFont("Helvetica-Bold", 12)
        c.setFillColorRGB(*_hex_to_rgb(PALETTE["white"]))
        c.drawString(left, y, "Key Recommendations")
        y -= 8 * mm
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(*_hex_to_rgb(PALETTE["muted_text"]))
        for rec in recs:
            wrapped = _wrap_text(rec, usable_w * 0.95, "Helvetica", 10)
            for j, ln in enumerate(wrapped):
                prefix = "• " if j == 0 else "  "
                c.drawString(left + 4 * mm, y, prefix + ln)
                y -= 5 * mm
            y -= 4 * mm

    # Notes
    notes = results.get("notes", "")
    if notes:
        if y < 80 * mm:
            c.showPage()
            c.setFillColorRGB(*_hex_to_rgb(PALETTE["bg_dark"]))
            c.rect(0, 0, width, height, stroke=0, fill=1)
            y = height - band_h - 10 * mm
        c.setFont("Helvetica-Bold", 12)
        c.setFillColorRGB(*_hex_to_rgb(PALETTE["white"]))
        c.drawString(left, y, "Notes")
        y -= 8 * mm
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(*_hex_to_rgb(PALETTE["muted_text"]))
        wrapped = _wrap_text(notes, usable_w * 0.95, "Helvetica", 10)
        for ln in wrapped:
            c.drawString(left + 4 * mm, y, ln)
            y -= 5 * mm

    # Footer line + metadata
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(*_hex_to_rgb(PALETTE["muted_text"]))
    c.drawString(left, 12 * mm, "T-Logic Consulting • AI-Enabled Readiness Assessment • Confidential")
    c.drawRightString(width - right, 12 * mm, f"Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

    c.save()
    data = buffer.getvalue()
    buffer.close()
    return data
