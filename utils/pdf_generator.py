# utils/pdf_generator.py

import io
import math
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


# ---------------------------------------------------------
# COLOR PALETTES (PASTEL DIMENSION COLORS)
# ---------------------------------------------------------

DIM_COLORS = {
    "Strategy": colors.HexColor("#F4B4B4"),        # Dusty Rose
    "People": colors.HexColor("#FCD0A4"),          # Apricot Cream
    "Technology": colors.HexColor("#FFF4B9"),      # Muted Lemon
    "Process": colors.HexColor("#B9F0C9"),         # Soft Sage
    "Data": colors.HexColor("#B3E5FC"),            # Sky Blue
    "Governance": colors.HexColor("#D7BDE2")       # Lavender Mist
}

# ---------------------------------------------------------
# READINESS LEVEL COLORS
# ---------------------------------------------------------
READINESS_LEVELS = {
    "Foundational": {
        "description": "First critical steps being laid",
        "color": colors.HexColor("#FFC107")  # Warm Amber
    },
    "Emerging": {
        "description": "Progress being made",
        "color": colors.HexColor("#4DB6AC")  # Soft Teal
    },
    "Reliable": {
        "description": "Consistent and dependable",
        "color": colors.HexColor("#42A5F5")  # Professional Blue
    },
    "Exceptional": {
        "description": "Best-in-class process performance",
        "color": colors.HexColor("#4CAF50")  # Deep Forest Green
    }
}


# ---------------------------------------------------------
# RADAR CHART DRAWING
# ---------------------------------------------------------
def draw_radar_chart(c, center_x, center_y, radius, labels, values, colors_map):
    """
    Draws a 6-axis radar chart (for your 6 dimension scores).
    Values must be normalized 0–1.
    """
    num_axes = len(labels)
    angle_step = 2 * math.pi / num_axes

    # Draw axes
    c.setStrokeColor(colors.white)
    for i in range(num_axes):
        angle = i * angle_step - math.pi / 2
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        c.line(center_x, center_y, x, y)

    # Draw polygon
    points = []
    for i, v in enumerate(values):
        angle = i * angle_step - math.pi / 2
        r = radius * v
        points.append((
            center_x + r * math.cos(angle),
            center_y + r * math.sin(angle)
        ))

    # Fill polygon
    c.setFillColor(colors.HexColor("#90CAF9"))
    c.setStrokeColor(colors.HexColor("#42A5F5"))
    c.setLineWidth(2)
    c.polygon(points, stroke=1, fill=1)


# ---------------------------------------------------------
# PAGE HEADER + FOOTER
# ---------------------------------------------------------
def draw_header_footer(c, logo_path, page_num):
    width, height = A4

    # Dark header orange band
    c.setFillColor(colors.HexColor("#FF8A00"))
    c.rect(0, height - 70, width, 70, fill=1, stroke=0)

    # Title placeholder — added dynamically later
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 45, c._page_title)

    # Logo at right
    if os.path.isfile(logo_path):
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, width - 120, height - 68, width=90, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    # FOOTER
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)

    # Left footer — website
    c.drawString(30, 20, "www.tlogic.consulting")

    # Right footer — page number
    c.drawRightString(width - 30, 20, f"Page {page_num}")


# ---------------------------------------------------------
# MAIN PDF GENERATOR
# ---------------------------------------------------------
def generate_pdf_report(
        results: dict,
        company_name: str = "[Your Company]",
        logo_path: str = "static/Tlogic_Logo4.png"
):
    """
    Generates a fully formatted PDF report.
    Returns PDF as bytes.
    """

    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Page counter
        page_num = 1

        # ---------------------------------------------------------
        # PAGE 1 — TITLE + EXECUTIVE SUMMARY + RADAR CHART
        # ---------------------------------------------------------
        c._page_title = f"AI-Enabled Process Readiness for: {company_name}"
        draw_header_footer(c, logo_path, page_num)

        # Executive summary text
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(40, height - 120, "Executive Summary")

        summary_y = height - 150
        c.setFont("Helvetica", 10)
        c.drawString(40, summary_y,
                     "Your readiness scores reflect performance across six foundational AI capability dimensions.")

        # Radar chart (centered)
        labels = [d["title"] for d in results["dimension_scores"]]
        values = [d["score"] / 5.0 for d in results["dimension_scores"]]

        draw_radar_chart(
            c,
            center_x=width / 2,
            center_y=height / 2 - 40,
            radius=120,
            labels=labels,
            values=values,
            colors_map=DIM_COLORS
        )

        c.showPage()
        page_num += 1

        # ---------------------------------------------------------
        # PAGE 2 — DIMENSION SCORES
        # ---------------------------------------------------------
        c._page_title = "Dimension Breakdown"
        draw_header_footer(c, logo_path, page_num)

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.white)
        c.drawString(40, height - 120,
                     "Your readiness scores across 6 dimensions:*")

        y = height - 160
        c.setFont("Helvetica", 10)

        for dim in results["dimension_scores"]:
            title = dim["title"]
            score = dim["score"]

            c.setFillColor(colors.white)
            c.drawString(40, y + 10, f"{title}: {score:.1f} / 5.0")

            # Bar
            c.setFillColor(DIM_COLORS.get(title, colors.grey))
            c.rect(40, y - 5, (score / 5.0) * 400, 12, fill=1, stroke=0)

            y -= 40

        # Disclaimer
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.white)
        c.drawString(40, 60,
                     "* This is a preliminary indicator based on subjective assessments and should not be treated as a "
                     "comprehensive readiness evaluation.")

        c.showPage()
        page_num += 1

        # ---------------------------------------------------------
        # PAGE 3 — READINESS LEVEL
        # ---------------------------------------------------------
        c._page_title = "Readiness Level"
        draw_header_footer(c, logo_path, page_num)

        readiness = results.get("readiness_band", {})
        level = readiness.get("label", "Emerging")
        desc = READINESS_LEVELS[level]["description"]
        col = READINESS_LEVELS[level]["color"]

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(col)
        c.drawString(40, height - 120, f"Readiness Level: {level}")

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.white)
        c.drawString(40, height - 150, desc)

        c.showPage()

        # ---------------------------------------------------------
        # FINALIZE PDF
        # ---------------------------------------------------------
        c.save()
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    except Exception as e:
        # Always return a minimal PDF even on error
        fallback = io.BytesIO()
        c = canvas.Canvas(fallback)
        c.drawString(50, 800, f"PDF generation error: {str(e)}")
        c.save()
        fallback.seek(0)
        return fallback.getvalue()
