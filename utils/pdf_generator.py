# utils/pdf_generator.py
"""
PDF generator for T-Logic AI-Enabled Process Readiness reports.

Call generate_pdf_report(results: dict, logo_path: str = "/static/TLogic_Logo4.png")
It returns bytes which can be written to a file or streamed to a web frontend.

Expected `results` structure (example):
{
  "overall_score": 22.5,              # total out of 30
  "dimension_scores": {
      "Process Maturity": 3.5,
      "Technology Infrastructure": 3.8,
      "Data Readiness": 2.9,
      "People & Culture": 3.7,
      "Leadership & Alignment": 4.2,
      "Governance & Risk": 3.1
  },
  "readiness_band": {"label": "Dependable"},   # one of Foundational, Emerging, Dependable, Exceptional
  "summary": "Executive summary text ...",
  "recommendations": {
      "Process Maturity": ["Rec 1", "Rec 2"],
      ...
  }
}
"""
from __future__ import annotations
import io
import os
import math
import tempfile
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import numpy as np

# ------------------------
# Color and baseline config
# ------------------------
PASTEL_COLORS = {
    "Process Maturity": "#DFA5A0",           # updated per user
    "Technology Infrastructure": "#FDD9B8",
    "Data Readiness": "#FFFB4B",
    "People & Culture": "#B9F0C9",
    "Leadership & Alignment": "#B3E5FC",
    "Governance & Risk": "#D7BDE2",
}

READINESS_LEVELS = {
    "Foundational": ("#DC2626", "First critical steps being laid."),
    "Emerging": ("#EAB308", "Meaningful progress being made."),
    "Dependable": ("#42A5F5", "Consistent and mostly reliable."),
    "Exceptional": ("#16A34A", "Best-in-class process performance."),
}

# Baseline (industry) averages start per your sample and update dynamically later
BASELINE_DIMENSION_AVG = {
    "Process Maturity": 3.2,
    "Technology Infrastructure": 3.4,
    "Data Readiness": 3.1,
    "People & Culture": 3.6,
    "Leadership & Alignment": 3.8,
    "Governance & Risk": 3.2,
}

SITE_URL = "www.tlogic.consulting"
COMPANY_COPY = "T-Logic Consulting Pvt. Ltd."


# ------------------------
# Helper drawing functions
# ------------------------
def _draw_header_footer(c: canvas.Canvas, title: str, logo_path: Optional[str], page_num: int) -> None:
    """Draw top header band + logo and bottom footer (site, company centered, page number right)."""
    width, height = A4
    # header band (dark blue)
    c.setFillColor(colors.HexColor("#0B5394"))  # dark blue header
    c.rect(0, height - 72, width, 72, stroke=0, fill=1)

    # Title (white)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(36, height - 44, title)

    # logo at top-right (fit to 90x60)
    if logo_path and os.path.isfile(logo_path):
        try:
            img = ImageReader(logo_path)
            c.drawImage(img, width - 140, height - 66, width=100, height=48, preserveAspectRatio=True, mask="auto")
        except Exception:
            # silently continue if image fails
            pass

    # Footer
    footer_y = 26
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(36, footer_y, SITE_URL)
    c.drawCentredString(width / 2.0, footer_y, COMPANY_COPY)
    c.drawRightString(width - 36, footer_y, f"Page {page_num}")


def _mm_to_pt(mm: float) -> float:
    """Utility if needing mm conversion (not actively used but handy)."""
    return mm * 2.834645669


def _draw_scoring_table(c: canvas.Canvas, x: int, y: int) -> None:
    """Draw a simplified scoring model table (static) into the canvas at (x,y)."""
    # We'll draw a small table describing ranges and labels
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Scoring Model (Total score out of 30)")
    table_y = y - 14
    # columns pos (left, mid, right)
    col1 = x
    col2 = x + 150
    col3 = x + 280

    # header row
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(col1, table_y, "Score Range")
    c.drawString(col2, table_y, "Readiness Level")
    c.drawString(col3, table_y, "Meaning")

    rows = [
        ("0 - 10", "Foundational", READINESS_LEVELS["Foundational"][1]),
        ("11 - 17", "Emerging", READINESS_LEVELS["Emerging"][1]),
        ("18 - 24", "Dependable", READINESS_LEVELS["Dependable"][1]),
        ("25 - 30", "Exceptional", READINESS_LEVELS["Exceptional"][1]),
    ]
    c.setFont("Helvetica", 9)
    yrow = table_y - 12
    for rng, lbl, meaning in rows:
        # label colored only
        c.setFillColor(colors.HexColor("#111111"))
        c.drawString(col1, yrow, rng)
        label_color = READINESS_LEVELS.get(lbl, ("#000000", ""))[0]
        c.setFillColor(colors.HexColor(label_color))
        c.drawString(col2, yrow, lbl)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(col3, yrow, meaning)
        yrow -= 12


def _draw_dimension_bars(c: canvas.Canvas, scores: Dict[str, float], start_x: int, start_y: int) -> int:
    """
    Draw per-dimension horizontal bars. Returns the y position after finishing.
    Bars use pastel colors defined in PASTEL_COLORS. Each dimension shows score (1 decimal).
    """
    width, _ = A4
    bar_max_width = width - start_x - 80
    spacing = 36
    y = int(start_y)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(start_x, y, "Dimension Breakdown")
    y -= 18

    c.setFont("Helvetica", 10)
    for dim, score in scores.items():
        # title + numeric
        label = f"{dim}"
        score_text = f"{score:.1f} / 5"
        c.setFillColor(colors.HexColor("#222222"))
        c.setFont("Helvetica", 10)
        c.drawString(start_x, y, label)
        c.drawRightString(start_x + bar_max_width + 60, y, score_text)

        # bar background
        bar_y = y - 12
        bar_h = 12
        c.setFillColor(colors.HexColor("#EEEEEE"))
        c.rect(start_x, bar_y, bar_max_width, bar_h, fill=1, stroke=0)

        # filled portion
        pct = float(score) / 5.0
        fill_w = float(bar_max_width) * max(0.0, min(1.0, pct))
        hexcolor = PASTEL_COLORS.get(dim, "#CCCCCC")
        c.setFillColor(colors.HexColor(hexcolor))
        c.rect(start_x, bar_y, fill_w, bar_h, fill=1, stroke=0)

        y -= spacing

    return int(y)


def _plot_difference_chart(dimension_scores: Dict[str, float], baseline: Dict[str, float]) -> str:
    """
    Create a difference chart (bars showing user score vs baseline as difference % or absolute).
    Returns a path to a PNG file.
    We'll draw a bar showing difference in percent (user - baseline) / baseline * 100.
    """
    dims = list(dimension_scores.keys())
    user_vals = [float(dimension_scores[d]) for d in dims]
    base_vals = [float(baseline.get(d, 0.0)) for d in dims]

    # differences in percentage points relative to baseline (avoid divide by zero)
    diffs = []
    for u, b in zip(user_vals, base_vals):
        if b == 0:
            diffs.append(0.0)
        else:
            diffs.append((u - b) / b * 100.0)

    # plot
    fig, ax = plt.subplots(figsize=(7.2, 2.2))  # wide, short
    indices = np.arange(len(dims))
    bar_colors = [PASTEL_COLORS.get(d, "#888888") for d in dims]
    ax.bar(indices, diffs, color=bar_colors, edgecolor="#333333")
    ax.axhline(0, color="#222222", linewidth=0.6)
    ax.set_xticks(indices)
    ax.set_xticklabels(dims, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Difference vs baseline (%)", fontsize=9)
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)

    plt.tight_layout()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp.name, dpi=150)
    plt.close(fig)
    return tmp.name


def _draw_recommendations(c: canvas.Canvas, recommendations: Dict[str, List[str]], start_x: int, start_y: int) -> int:
    """
    Draw recommendations grouped by dimension. Returns y coordinate after content.
    """
    y = int(start_y)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(start_x, y, "Recommended Actions")
    y -= 18

    c.setFont("Helvetica", 10)
    for dim, recs in (recommendations or {}).items():
        # dimension header
        c.setFillColor(colors.HexColor("#111111"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(start_x, y, f"{dim}:")
        y -= 14
        c.setFont("Helvetica", 10)
        for r in recs:
            # bullet point
            c.drawString(start_x + 8, y, f"• {r}")
            y -= 12
            if y < 80:
                c.showPage()
                # restore header/footer later by caller
                y = int(A4[1]) - 120
        y -= 6

    return int(y)


# ------------------------
# Public generator
# ------------------------
def generate_pdf_report(
    results: Dict[str, Any],
    logo_path: str = "/static/TLogic_Logo4.png",
) -> bytes:
    """
    Main entrypoint. Returns PDF as bytes.
    """
    # Validate minimal structure
    if not isinstance(results, dict):
        raise ValueError("results must be a dict")

    # Ensure dimension names in expected order
    dims_expected = list(BASELINE_DIMENSION_AVG.keys())
    dim_scores = results.get("dimension_scores", {})
    # If missing dims, fill with 0.0
    dimension_scores = {d: float(dim_scores.get(d, 0.0)) for d in dims_expected}

    overall_score = float(results.get("overall_score", sum(dimension_scores.values())))
    readiness_label = results.get("readiness_band", {}).get("label", "Foundational")
    executive_summary = str(results.get("summary", "") or "")
    recommendations = results.get("recommendations", {}) or {}

    # Compose title
    company_name = results.get("company_name", results.get("company", "[Your Company]"))
    page_title = f"AI-Enabled Process Readiness Assessment — {company_name}"

    # Canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    try:
        page = 1
        # ----- PAGE 1: TITLE + EXEC SUMMARY + SCORING MODEL -----
        _draw_header_footer(c, page_title, logo_path, page)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#111111"))
        c.drawString(36, height - 110, "Executive Summary")

        # summary box
        box_x = 36
        box_w = width - 72
        box_h = 110
        summary_y = height - 136 - box_h + 12
        c.setFillColor(colors.white)
        c.rect(box_x, summary_y, box_w, box_h, fill=1, stroke=1)
        c.setFont("Helvetica", 10)
        text = c.beginText(box_x + 8, summary_y + box_h - 18)
        for line in executive_summary.splitlines() or ["(No executive summary provided)"]:
            text.textLine(line)
        c.drawText(text)

        # Top boxes: Overall readiness, Readiness %, Readiness label
        # compute readiness %
 (overall_pct := (overall_score / 30.0) * 100.0)
        # small numeric boxes
        box_h2 = 56
        bx_left = width - 36 - 340
        by = height - 92
        # box 1: Overall
        c.setFillColor(colors.HexColor("#F5F5F5"))
        c.rect(bx_left, by - box_h2 + 6, 100, box_h2, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#111111"))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(bx_left + 8, by - 18, "Overall Readiness")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(bx_left + 8, by - 36, f"{overall_score:.1f} / 30")

        # box 2: Percent
        bx2 = bx_left + 110
        c.setFillColor(colors.HexColor("#F5F5F5"))
        c.rect(bx2, by - box_h2 + 6, 100, box_h2, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#111111"))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(bx2 + 8, by - 18, "Readiness %")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(bx2 + 8, by - 36, f"{overall_pct:.0f}%")

        # box 3: Label (colored)
        bx3 = bx2 + 110
        c.setFillColor(colors.HexColor("#F5F5F5"))
        c.rect(bx3, by - box_h2 + 6, 120, box_h2, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(bx3 + 8, by - 18, "Indicator")
        label_color = READINESS_LEVELS.get(readiness_label, ("#000000", ""))[0]
        c.setFillColor(colors.HexColor(label_color))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(bx3 + 8, by - 36, readiness_label)
        # small grey description under label (black text)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#444444"))
        label_desc = READINESS_LEVELS.get(readiness_label, ("#000000", ""))[1]
        c.drawString(bx3 + 8, by - 52, label_desc)

        # scoring model table (left side near summary)
        _draw_scoring_table(c, 36, height - 170)

        c.showPage()
        page += 1

        # ----- PAGE 2: DIMENSION BREAKDOWN + BENCHMARK DIFF -----
        _draw_header_footer(c, page_title, logo_path, page)
        # draw dimension bars
        y_after = _draw_dimension_bars(c, dimension_scores, 36, int(height - 120))

        # Add industry benchmark difference chart
        chart_path = _plot_difference_chart(dimension_scores, BASELINE_DIMENSION_AVG)
        # place chart below bars
        img_w = width - 72
        img_h = 160
        c.drawImage(chart_path, 36, y_after - img_h - 12, width=img_w, height=img_h, preserveAspectRatio=True, mask="auto")

        # small footnote about benchmark derivation
        footnote = "Industry baseline derived from initial sample (20 participants) and will update as sample grows."
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(36, y_after - img_h - 28, footnote)

        c.showPage()
        page += 1

        # ----- PAGE 3: RECOMMENDATIONS -----
        _draw_header_footer(c, page_title, logo_path, page)
        _draw_recommendations(c, recommendations, 36, int(height - 120))

        c.showPage()
        c.save()

        # cleanup temporary files (chart)
        try:
            if os.path.exists(chart_path):
                os.remove(chart_path)
        except Exception:
            pass

        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    except Exception as e:
        # On error produce a small fallback PDF describing the error (safe for logs)
        try:
            c = canvas.Canvas(buffer, pagesize=A4)
            c.setFont("Helvetica", 10)
            c.drawString(36, A4[1] - 36, "PDF generation failed. Error message included below.")
            c.drawString(36, A4[1] - 56, str(e))
            c.save()
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
        except Exception:
            # as last resort return an empty bytes object
            return b""
