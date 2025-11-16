import io, os, math
from typing import Optional, Dict, Any
from typing import Any, Dict
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, Polygon, String
from reportlab.graphics import renderPDF


# ---------------------------------------------------------
# T-LOGIC COLOR SYSTEM (matches the app)
# ---------------------------------------------------------
TL_COLORS = {
    "Strategy":    colors.HexColor("#E63946"),  # red
    "People":      colors.HexColor("#F77F00"),  # orange
    "Technology":  colors.HexColor("#FFBA08"),  # yellow
    "Process":     colors.HexColor("#43AA8B"),  # green
    "Data":        colors.HexColor("#4D9DE0"),  # blue
    "Governance":  colors.HexColor("#8367C7"),  # purple
}

READINESS_COLORS = {
    "Nascent":     colors.HexColor("#E63946"),
    "Emerging":    colors.HexColor("#F77F00"),
    "Established": colors.HexColor("#43AA8B"),
    "Advanced":    colors.HexColor("#4D9DE0"),
}


# --------------------------------------------------------------------
# 🔷 RADAR CHART (SPIDER CHART) — ReportLab vector drawing
# --------------------------------------------------------------------
def draw_radar_chart(dimensions, max_value=5):
    """
    Returns a ReportLab Drawing object containing the radar chart.
    Dimensions: list of dicts with keys: title, score
    """
    d = Drawing(300, 300)
    center_x, center_y = 150, 150
    radius = 100

    angles = []
    n = len(dimensions)

    for i in range(n):
        angles.append((2 * math.pi / n) * i - math.pi / 2)

    # Draw axes
    for ang in angles:
        x = center_x + radius * math.cos(ang)
        y = center_y + radius * math.sin(ang)
        d.add(Polygon([center_x, center_y, x, y], strokeColor=colors.grey))

    # Draw outline polygon
    outline_points = []
    for ang in angles:
        x = center_x + radius * math.cos(ang)
        y = center_y + radius * math.sin(ang)
        outline_points.extend([x, y])

    d.add(Polygon(outline_points, strokeColor=colors.black, fillColor=None))

    # Draw score polygon
    score_points = []
    for item, ang in zip(dimensions, angles):
        score = item["score"]
        pct = score / max_value
        x = center_x + radius * pct * math.cos(ang)
        y = center_y + radius * pct * math.sin(ang)
        score_points.extend([x, y])

    d.add(Polygon(score_points, strokeColor=colors.HexColor("#43AA8B"),
                  fillColor=colors.HexColor("#43AA8B"), fillOpacity=0.25))

    # Add labels
    for item, ang in zip(dimensions, angles):
        lx = center_x + (radius + 18) * math.cos(ang)
        ly = center_y + (radius + 18) * math.sin(ang)
        d.add(String(lx, ly, item["title"], fontSize=9))

    return d


# --------------------------------------------------------------------
# 🔶 MAIN PDF GENERATOR
# --------------------------------------------------------------------
def generate_pdf_report(
    results: Dict[str, Any],
    company_name: Optional[str] = None,
    subtitle: Optional[str] = None,
    primary_color: Optional[str] = None,
    logo_path: Optional[str] = None,
    font_path: Optional[str] = None
    ) -> bytes:


    # Fallback name
    if not company_name or company_name.strip() == "":
        company_name = "[Your Company]"

    title_text = f"AI-Enabled Process Readiness for: {company_name}"

    # PDF setup
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 22 * mm

    # ---------------------------------------------------------
    # HEADER BAND
    # ---------------------------------------------------------
    HEADER_ORANGE = colors.HexColor("#F77F00")
    header_h = 28 * mm

    pdf.setFillColor(HEADER_ORANGE)
    pdf.rect(0, height - header_h, width, header_h, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(margin, height - header_h + 10 * mm, title_text)

    # Logo
    if logo_path and os.path.isfile(logo_path):
        try:
            img = ImageReader(logo_path)
            pdf.drawImage(img, width - margin - 32 * mm,
                          height - header_h + 4 * mm,
                          width=32 * mm, preserveAspectRatio=True,
                          mask="auto")
        except:
            pass

    y = height - header_h - 20 * mm

    # ---------------------------------------------------------
    # EXECUTIVE SUMMARY
    # ---------------------------------------------------------
    readiness_label = results.get("readiness_band", {}).get("label", "Unknown")
    readiness_color = READINESS_COLORS.get(readiness_label, colors.black)

    total = results.get("total", 0)
    percentage = results.get("percentage", 0)

    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(colors.black)
    pdf.drawString(margin, y, "Executive Summary")
    y -= 8 * mm

    pdf.setFont("Helvetica", 11)
    pdf.drawString(margin, y, f"• Readiness Level: {readiness_label}")
    y -= 6 * mm
    pdf.drawString(margin, y, f"• Overall Score: {percentage}% ({total}/30)")
    y -= 6 * mm

    pdf.drawString(margin, y, "• Strengths and Opportunities identified across six readiness dimensions.")
    y -= 12 * mm

    # ---------------------------------------------------------
    # REMOVE “indicative”
    # ---------------------------------------------------------
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Your readiness scores across 6 dimensions:*")
    y -= 10 * mm

    # ---------------------------------------------------------
    # OVERALL SCORE BAR (text only — spider chart on next page)
    # ---------------------------------------------------------
    pdf.setFont("Helvetica-Bold", 12)
    pdf.setFillColor(readiness_color)
    pdf.drawString(margin, y, f"Readiness Level: {readiness_label}")
    y -= 10 * mm

    pdf.setFillColor(colors.black)
    pdf.drawString(margin, y, f"Overall Score: {percentage}% ({total}/30)")
    y -= 15 * mm

    # ---------------------------------------------------------
    # DISCLAIMER
    # ---------------------------------------------------------
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.setFillColor(colors.HexColor("#444444"))
    pdf.drawString(
        margin,
        y,
        "* This is a preliminary indicator based on subjective assessments and "
        "is not meant to replace a rigorous analysis of organizational AI preparedness."
    )
    y -= 15 * mm

    # ---------------------------------------------------------
    # DIMENSION BREAKDOWN
    # ---------------------------------------------------------
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(margin, y, "Dimension Breakdown")
    y -= 10 * mm

    dims = results.get("dimension_scores", [])
    bar_h = 7 * mm
    bar_w = width - (2 * margin) - 35 * mm

    for d in dims:
        name = d.get("title", "Dimension")
        score = float(d.get("score", 0))
        pct = (score / 5) * 100

        color = TL_COLORS.get(name, colors.grey)

        # Label
        pdf.setFont("Helvetica-Bold", 11)
        pdf.setFillColor(colors.black)
        pdf.drawString(margin, y, name)

        # Bar (background)
        pdf.setFillColor(colors.Color(0.9, 0.9, 0.9))
        pdf.rect(margin, y - bar_h + 2, bar_w, bar_h, fill=1)

        # Bar (fill)
        pdf.setFillColor(color)
        pdf.rect(margin, y - bar_h + 2, bar_w * (pct / 100), bar_h, fill=1)

        # Percentage text
        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawRightString(margin + bar_w + 30 * mm, y, f"{int(pct)}%")

        y -= 12 * mm

        if y < 40 * mm:  # New page if needed
            pdf.showPage()
            y = height - margin

    # ---------------------------------------------------------
    # PAGE BREAK FOR SPIDER CHART
    # ---------------------------------------------------------
    pdf.showPage()
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(margin, height - margin, "Readiness Radar Chart")

    # Draw radar chart
    radar = draw_radar_chart(dims)
    renderPDF.draw(radar, pdf, margin, height - 330)

    # ---------------------------------------------------------
    # NEXT STEPS (auto generated)
    # ---------------------------------------------------------
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(margin, 260, "Next Steps")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(margin, 240, "Based on your results, consider:")

    line_y = 220
    next_steps = []

    # Rules for next steps
    for dim in dims:
        name = dim["title"]
        score = dim["score"]

        if score <= 2:
            next_steps.append(f"• Prioritize strengthening {name.lower()} (low score).")

    if readiness_label in ["Nascent", "Emerging"]:
        next_steps.append("• Establish foundational governance and AI strategy structures.")
    else:
        next_steps.append("• Scale successful initiatives and optimize cross-functional processes.")

    for step in next_steps:
        pdf.drawString(margin, line_y, step)
        line_y -= 12

    # ---------------------------------------------------------
    # FOOTER + PAGE NUMBERS
    # ---------------------------------------------------------
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.setFillColor(colors.HexColor("#333333"))
    pdf.drawCentredString(width / 2, 12 * mm, "www.tlogic.consulting")

    pdf.save()
    return buffer.getvalue()

