import io
import os
from typing import Dict, Any
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader


# -------------------------------------------------------
# Pastel colors for dimension bars (exact from app)
# -------------------------------------------------------
PASTEL_COLORS = {
    "Process Maturity": "#F4B4B4",
    "Technology Infrastructure": "#FCD0A4",
    "Data Readiness": "#FFF4B9",
    "People & Culture": "#B9F0C9",
    "Leadership & Alignment": "#B3E5FC",
    "Governance & Risk": "#D7BDE2",
}

# Readiness Levels
READINESS_LEVELS = {
    "Foundational": ("#FFC107", "Early stage capability foundation"),
    "Emerging": ("#FF8A65", "Growing capabilities with visible traction"),
    "Reliable": ("#42A5F5", "Consistent and well-governed processes"),
    "Exceptional": ("#4CAF50", "High-performing, scalable and AI-ready"),
}


# -------------------------------------------------------
# Header + Footer
# -------------------------------------------------------
def draw_header_footer(
    c: canvas.Canvas,
    page_title: str,
    logo_path: str,
    page_num: int
) -> None:

    width, height = A4

    # Header band
    c.setFillColor(colors.HexColor("#FF8A00"))
    c.rect(0, height - 70, width, 70, fill=1, stroke=0)

    # Title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(30, height - 45, page_title)

    # Logo (right)
    if logo_path and os.path.isfile(logo_path):
        try:
            img = ImageReader(logo_path)
            c.drawImage(img, width - 130, height - 62,
                        width=100, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    # Footer
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(30, 25, "www.tlogic.consulting")
    c.drawCentredString(width / 2, 25, "T-Logic Consulting Pvt. Ltd.")
    c.drawRightString(width - 30, 25, f"Page {page_num}")


# -------------------------------------------------------
# Dimension Bars
# -------------------------------------------------------
def draw_dimension_bars(
    c: canvas.Canvas,
    scores: Dict[str, float],
    start_y: float
) -> float:

    width, _ = A4
    bar_w = width - 120
    bar_h = 22
    x = 60
    y = start_y

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(40, y + 20, "Dimension Scores")

    c.setFont("Helvetica", 11)

    for dim, score in scores.items():
        y -= 45
        pct = min(max(score / 5.0, 0), 1)

        # Label
        c.setFillColor(colors.black)
        c.drawString(x, y + 22, f"{dim}: {score:.1f} / 5")

        # Background bar
        c.setFillColor(colors.HexColor("#DDDDDD"))
        c.rect(x, y, bar_w, bar_h, fill=1, stroke=0)

        # Filled pastel bar
        c.setFillColor(colors.HexColor(PASTEL_COLORS.get(dim, "#AAAAAA")))
        c.rect(x, y, bar_w * pct, bar_h, fill=1, stroke=0)

    return y - 25


# -------------------------------------------------------
# Recommendations Engine (Simple)
# -------------------------------------------------------
def generate_recommendations(
    overall: float,
    dims: Dict[str, float]
) -> list[str]:

    steps: list[str] = []

    if overall < 2.5:
        steps.append("Strengthen foundational processes before scaling AI initiatives.")
    elif overall < 3.5:
        steps.append("Prioritize areas scoring below 3.0 for targeted improvements.")
    else:
        steps.append("Processes are mature enough to begin structured AI adoption.")

    # Per-dimension suggestions
    for dim, score in dims.items():
        if score < 3:
            steps.append(f"Improve '{dim}' — score is {score:.1f}/5, below readiness threshold.")

    if not steps:
        steps.append("Maintain continuous improvement to preserve high readiness levels.")

    return steps


# -------------------------------------------------------
# PDF Generator (FINAL, CLEAN, NO ERRORS)
# -------------------------------------------------------
def generate_pdf_report(
    results: Dict[str, Any],
    company_name: str,
    tagline: str,
    logo_path: str
) -> bytes:

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    page = 1

    page_title = f"AI-Enabled Process Readiness: {company_name}"

    # ------------------------------
    # PAGE 1 — EXEC SUMMARY
    # ------------------------------
    draw_header_footer(c, page_title, logo_path, page)

    overall = float(results["overall_score"])
    dim_scores = results["dimension_scores"]

    readiness_label = results["readiness_band"]["label"]
    readiness_color = READINESS_LEVELS[readiness_label][0]
    readiness_desc = READINESS_LEVELS[readiness_label][1]

    # Title
    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 120, "Executive Summary")

    # Readiness Level
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor(readiness_color))
    c.drawString(
        40,
        height - 155,
        f"Overall Readiness: {readiness_label} ({overall:.1f}/5)"
    )

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    c.drawString(40, height - 175, readiness_desc)

    # Tagline
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(40, height - 205, tagline)

    c.showPage()
    page += 1

    # ------------------------------
    # PAGE 2 — DIMENSION BARS
    # ------------------------------
    draw_header_footer(c, page_title, logo_path, page)

    y_end = draw_dimension_bars(c, dim_scores, height - 110)

    # Disclaimer
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(
        40,
        y_end,
        "* Preliminary readiness indicator — not a substitute for full organizational assessment."
    )

    c.showPage()
    page += 1

    # ------------------------------
    # PAGE 3 — RECOMMENDATIONS
    # ------------------------------
    draw_header_footer(c, page_title, logo_path, page)

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(40, height - 110, "Key Recommendations")

    c.setFont("Helvetica", 11)
    recs = generate_recommendations(overall, dim_scores)

    y = height - 145
    for rec in recs:
        c.drawString(50, y, f"• {rec}")
        y -= 20
        if y < 80:
            c.showPage()
            page += 1
            draw_header_footer(c, page_title, logo_path, page)
            y = height - 120

    c.showPage()

    c.save()
    return buffer.getvalue()
