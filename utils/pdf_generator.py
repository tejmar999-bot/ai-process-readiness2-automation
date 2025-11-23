# utils/pdf_generator.py
"""
Production-ready PDF generator for T-Logic AI-Enabled Process Readiness (2 pages).

Public API:
    generate_pdf_report(results: dict, company_name: str, tagline: str, logo_path: Optional[str], industry_baseline: Optional[Sequence[float]]) -> bytes

Notes:
- results expected keys:
    - overall_score: float (0..5)
    - readiness_band: { "label": str, "description": str, "color": "#hex" }   # optional; derived if absent
    - dimension_scores: { "<Dimension Name>": float, ... }  (1..5)
    - dimension_notes: { "<Dimension Name>": str }          # optional
    - recommendations: [str, ...]                           # optional
    - notes / executive_summary: str                        # optional

- industry_baseline: optional list of 6 floats (one per dimension) to seed industry averages.
  If not provided, code uses the default baseline from your sample of 20 participants.
"""

import io
import os
from typing import Dict, Any, Optional, Sequence, List
from textwrap import wrap
from statistics import mean

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

import matplotlib.pyplot as plt
import numpy as np

# ---------------------------
# Colors & master data
# ---------------------------
# Pastel colors for the six dimensions (use the exact palette you provided)
PASTEL_DIMENSION_COLORS: Dict[str, str] = {
    "Process Maturity": "#F4B4B4",
    "Technology Infrastructure": "#FCD0A4",
    "Data Readiness": "#FFF4B9",
    "People & Culture": "#B9F0C9",
    "Leadership & Alignment": "#B3E5FC",
    "Governance & Risk": "#D7BDE2",
}

# Readiness levels mapping
READINESS_LEVELS: Dict[str, tuple] = {
    "Foundational": ("#FFC107", "First critical steps being laid."),
    "Emerging": ("#FF8A65", "Progress being made."),
    "Reliable": ("#42A5F5", "Consistent and dependable."),
    "Exceptional": ("#4CAF50", "Best-in-class process performance."),
}

# Default industry baseline (your sample of 20 participants)
DEFAULT_INDUSTRY_BASELINE = [3.2, 3.4, 3.1, 3.6, 3.8, 3.2]

WEBSITE = "www.tlogic.consulting"
COPYRIGHT = "T-Logic Consulting Pvt. Ltd."


# ---------------------------
# Helpers
# ---------------------------
def _safe_float(x: Optional[Any]) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0


def _wrap(text: str, width: int = 100) -> List[str]:
    if not text:
        return []
    return wrap(text, width)


# ---------------------------
# Radar chart (PNG bytes)
# ---------------------------
def _create_radar_png(dim_labels: Sequence[str], dim_values: Sequence[float], pastel_colors: Sequence[str]) -> bytes:
    """
    Create a radar chart PNG in memory using matplotlib and return bytes.
    dim_values expected in 0..5 scale.
    pastel_colors: list of colors for markers/area per axis (same length as labels).
    """
    # ensure lengths match
    n = len(dim_labels)
    values = [max(0.0, min(5.0, float(v))) for v in dim_values]
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(4.0, 4.0), dpi=160)
    ax = fig.add_subplot(111, polar=True)

    # orient to top
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dim_labels, fontsize=9)

    # radius
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=7)

    # grid style
    ax.grid(color="#E6E6E6", linestyle="--", linewidth=0.6)

    # plot
    ax.plot(angles, values, linewidth=2, color="#333333")
    ax.fill(angles, values, color="#6EC6FF", alpha=0.22)

    # color-coded markers at each axis value (use pastel colors)
    for idx, (theta, r, col) in enumerate(zip(angles[:-1], values[:-1], pastel_colors)):
        ax.scatter([theta], [r], color=col, s=40, zorder=10)

    # Save to bytes buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# ---------------------------
# Drawing helpers (header/footer/bars)
# ---------------------------
def _draw_header(c: canvas.Canvas, title: str, logo_path: Optional[str], header_color: str = "#0b3d91"):
    """
    Draws a dark-blue header bar and title; logo on the right if provided.
    header_color defaults to dark blue (as per mockup).
    """
    w, h = A4
    # header rectangle
    c.setFillColor(colors.HexColor(header_color))
    c.rect(0, h - 72, w, 72, fill=1, stroke=0)

    # title left
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(36, h - 44, title)

    # logo (right)
    if logo_path:
        try:
            if isinstance(logo_path, (bytes, bytearray)):
                img = ImageReader(io.BytesIO(logo_path))  # type: ignore[name-defined]
            else:
                if os.path.isfile(logo_path):
                    img = ImageReader(logo_path)
                else:
                    img = None
            if img:
                c.drawImage(img, w - 140, h - 64, width=110, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass


def _draw_footer(c: canvas.Canvas, page_num: int):
    w, h = A4
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(36, 18, WEBSITE)                # left
    c.drawCentredString(w / 2.0, 18, COPYRIGHT)  # center
    c.drawRightString(w - 36, 18, f"Page {page_num}")  # right


def _draw_bar(c: canvas.Canvas, x: float, y: float, w: float, h: float, pct: float, color_hex: str):
    # background
    c.setFillColor(colors.HexColor("#EEEEEE"))
    c.rect(x, y, w, h, fill=1, stroke=0)
    # fill
    fill_w = max(0.0, min(w, w * pct))
    c.setFillColor(colors.HexColor(color_hex))
    c.rect(x, y, fill_w, h, fill=1, stroke=0)


# ---------------------------
# Recommendations generator (simple rules)
# ---------------------------
def _recommendations_from_scores(overall: float, dim_scores: Dict[str, float]) -> List[str]:
    recs: List[str] = []
    if overall < 2.5:
        recs += [
            "Prioritise foundational process documentation and basic data capture.",
            "Run 1-2 small pilots to prove value and build momentum.",
            "Assign process owners and capture baseline KPIs."
        ]
    elif overall < 3.5:
        recs += [
            "Improve data pipelines and monitoring for key sources.",
            "Upskill a cross-functional team to lead repeatable pilots.",
            "Prioritise automation in high-volume manual areas."
        ]
    elif overall < 4.2:
        recs += [
            "Standardize deployment and governance for scalable operations.",
            "Scale successful pilots into production with observability.",
            "Invest in tooling and process monitoring."
        ]
    else:
        recs += [
            "Share best-practice playbooks and scale internally.",
            "Explore advanced AI ops and industrialize successful use cases.",
            "Build a Centre of Excellence to accelerate innovation."
        ]

    # add dimension-specific calling-outs
    for k, v in sorted(dim_scores.items(), key=lambda kv: kv[1]):
        if v < 3.0:
            recs.append(f"Target improvements in {k} (current {v:.1f}/5). Set measurable milestones.")
    return recs


# ---------------------------
# Main public generator
# ---------------------------
def generate_pdf_report(
    results: Dict[str, Any],
    company_name: str,
    tagline: Optional[str] = None,
    logo_path: Optional[str] = None,
    industry_baseline: Optional[Sequence[float]] = None,
) -> Optional[bytes]:
    """
    Generate a 2-page PDF report and return bytes.
    - results: dict as described at top of file
    - industry_baseline: optional list[6] for dimension baseline; otherwise DEFAULT_INDUSTRY_BASELINE is used
    """
    try:
        tagline = tagline or "AI-Enabled Process Readiness"
        overall_score = _safe_float(results.get("overall_score", 0.0))
        dim_scores_map: Dict[str, float] = {k: _safe_float(v) for k, v in (results.get("dimension_scores") or {}).items()}

        # Ensure order of dims follows PASTEL_DIMENSION_COLORS when possible
        dims_order = [d for d in PASTEL_DIMENSION_COLORS.keys() if d in dim_scores_map]
        if not dims_order:
            dims_order = list(dim_scores_map.keys())

        # Industry baseline handling
        baseline = list(industry_baseline) if industry_baseline else list(DEFAULT_INDUSTRY_BASELINE)
        # compute industry overall average (mean of baseline dims)
        industry_overall = mean([_safe_float(x) for x in baseline]) if baseline else 0.0

        # readiness label and color (prefer provided band)
        band = results.get("readiness_band") or {}
        label = band.get("label") if isinstance(band, dict) else None
        if not label:
            # derive label by score thresholds
            if overall_score < 2.5:
                label = "Foundational"
            elif overall_score < 3.5:
                label = "Emerging"
            elif overall_score < 4.2:
                label = "Reliable"
            else:
                label = "Exceptional"
        color_hex, label_desc = READINESS_LEVELS.get(label, ("#999999", ""))

        # PDF canvas
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        w, h = A4
        page = 1
        title = f"{tagline} for: {company_name or '[Your Company]'}"

        # ---------- PAGE 1 (Executive summary + overall + radar) ----------
        _draw_header(c, title, logo_path, header_color="#0b3d91")  # dark blue header per mockup

        # Executive Summary box (left)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(40, h - 110, "Executive Summary")

        exec_notes = results.get("notes") or results.get("executive_summary") or ""
        c.setFont("Helvetica", 10)
        ytext = h - 130
        if exec_notes:
            for i, line in enumerate(_wrap(exec_notes, 90)[:8]):
                c.drawString(40, ytext - (i * 12), line)
            ytext = ytext - (min(8, len(_wrap(exec_notes, 90))) * 12) - 8
        else:
            c.setFont("Helvetica-Oblique", 9)
            c.setFillColor(colors.HexColor("#666666"))
            c.drawString(40, ytext, "No executive summary provided.")
            ytext -= 20

        # Overall readiness block (left below summary)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor(color_hex))
        c.drawString(40, ytext, f"Overall Readiness: {label} — {overall_score:.1f} / 5")
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(40, ytext - 16, label_desc)

        # Performance vs industry (right area)
        right_x = w - 260
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(right_x, h - 140, "Performance vs Industry (baseline)")
        c.setFont("Helvetica", 10)
        c.drawString(right_x, h - 156, f"Your score: {overall_score:.1f} / 5")
        c.drawString(right_x, h - 170, f"Industry avg: {industry_overall:.1f} / 5")
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(right_x, h - 188, "Baseline based on sample N=20 participants (see footnote).")

        # Radar chart centered (use dim labels & values)
        dim_labels = dims_order
        dim_values = [dim_scores_map.get(k, 0.0) for k in dim_labels]
        pastel_cols = [PASTEL_DIMENSION_COLORS.get(k, "#BBBBBB") for k in dim_labels]
        radar_png = _create_radar_png(dim_labels, dim_values, pastel_cols)
        # draw radar
        try:
            img = ImageReader(io.BytesIO(radar_png))
            radar_w = 280
            radar_h = 280
            radar_x = (w - radar_w) / 2.0
            radar_y = h - 470
            c.drawImage(img, radar_x, radar_y, width=radar_w, height=radar_h, preserveAspectRatio=True, mask="auto")
        except Exception:
            # fallback: ignore radar if embedding fails
            pass

        _draw_footer(c, page)
        c.showPage()
        page += 1

        # ---------- PAGE 2 (Dimension bands + recommendations + footnote) ----------
        _draw_header(c, title, logo_path, header_color="#0b3d91")
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(40, h - 100, "Dimension Scores & Recommendations")

        # iterate dims and draw bar + description + numeric
        y = h - 130
        bar_x = 40
        bar_w = w - 220
        bar_h = 14
        gap = 58

        for dim in dim_labels:
            score = _safe_float(dim_scores_map.get(dim, 0.0))
            pct = max(0.0, min(1.0, score / 5.0))
            color_dim = PASTEL_DIMENSION_COLORS.get(dim, "#CCCCCC")
            # Title + score
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor("#222222"))
            c.drawString(bar_x, y, f"{dim} — {score:.1f} / 5")
            # short performance description (from results.dimension_notes or default mapping)
            descr = (results.get("dimension_notes") or {}).get(dim) or ""
            if not descr:
                # fallback to a generic one-line description available in mapping above if present
                descr = ""
            # Draw progress bar
            _draw_bar(c, bar_x, y - 22, bar_w, bar_h, pct, color_dim)
            # Description below bar (one line)
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.HexColor("#444444"))
            if descr:
                for i, ln in enumerate(_wrap(descr, 90)[:2]):
                    c.drawString(bar_x, y - 40 - (i * 11), ln)
            y -= gap
            if y < 120:
                _draw_footer(c, page)
                c.showPage()
                page += 1
                _draw_header(c, title, logo_path, header_color="#0b3d91")
                y = h - 120

        # Recommendations section (compact)
        recs = results.get("recommendations") or _recommendations_from_scores(overall_score, dim_scores_map)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(40, y, "Recommendations & Next Steps")
        y -= 18
        c.setFont("Helvetica", 10)
        for r in recs:
            wrapped = _wrap(r, 100)
            c.drawString(46, y, u"\u2022 " + wrapped[0])
            y -= 14
            for part in wrapped[1:]:
                c.drawString(60, y, part)
                y -= 12
            y -= 6
            if y < 100:
                _draw_footer(c, page)
                c.showPage()
                page += 1
                _draw_header(c, title, logo_path, header_color="#0b3d91")
                y = h - 120

        # Footnote explaining industry baseline derivation
        footnote = (
            "Footnote: Industry baseline values shown above were derived from an internal sample "
            "of N=20 participants collected as a baseline. Aggregation excludes extreme outliers "
            "(all-1 or all-5 responses) and reports the arithmetic mean per dimension. Replace with "
            "your production benchmark dataset as it becomes available."
        )
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(40, 72, footnote)

        _draw_footer(c, page)
        c.save()

        buffer.seek(0)
        return buffer.getvalue()

    except Exception as exc:
        # Leaf a minimal PDF with error text to ease debugging on Streamlit
        try:
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, 800, "PDF generation failed. See logs for details.")
            c.drawString(40, 780, str(exc))
            c.showPage()
            c.save()
            buf.seek(0)
            return buf.getvalue()
        except Exception:
            return None
