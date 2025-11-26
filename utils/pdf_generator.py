# utils/pdf_generator.py

import io
import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import tempfile

# ----------------------------------------------------------
# BRAND COLORS
# ----------------------------------------------------------
HEADER_COLOR = "#003B73"  # Dark blue header from your mock-up

# Updated pastel colors
PASTEL_COLORS = {
    "Process Maturity": "#DFA5A0",
    "Technology Infrastructure": "#FDD9B8",
    "Data Readiness": "#FFFB4B",
    "People & Culture": "#B9F0C9",
    "Leadership & Alignment": "#B3E5FC",
    "Governance & Risk": "#D7BDE2",
}

# Readiness levels (0–30 scoring)
READINESS_LEVELS = [
    {
        "min": 0,
        "max": 10,
        "label": "Foundational",
        "color": "#DC2626",
        "description": "First critical steps being laid."
    },
    {
        "min": 11,
        "max": 17,
        "label": "Emerging",
        "color": "#EAB308",
        "description": "Meaningful progress being made."
    },
    {
        "min": 18,
        "max": 24,
        "label": "Dependable",
        "color": "#42A5F5",
        "description": "Consistent & dependable performance."
    },
    {
        "min": 25,
        "max": 30,
        "label": "Exceptional",
        "color": "#16A34A",
        "description": "Best-in-class process performance."
    },
]

# Industry baseline for your 20-participant sample
BASELINE_AVG = {
    "Process Maturity": 3.2,
    "Technology Infrastructure": 3.4,
    "Data Readiness": 3.1,
    "People & Culture": 3.6,
    "Leadership & Alignment": 3.8,
    "Governance & Risk": 3.2,
}

# ----------------------------------------------------------
# RADAR CHART GENERATOR — light theme, no black background
# ----------------------------------------------------------
def generate_radar_chart(user_scores: Dict[str, float]) -> str:
    categories = list(user_scores.keys())
    values = list(user_scores.values())
    values.append(values[0])

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles.append(angles[0])

    fig = plt.figure(figsize=(5, 5), facecolor="white")
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor("white")

    ax.set_theta_offset(float(np.pi / 2))
    ax.set_theta_direction(-1.0)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)

    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_ylim(0, 5)
    ax.grid(color="#CCCCCC")

    # plot
    ax.plot(angles, values, linewidth=2, color="#003B73")
    ax.fill(angles, values, color="#6699CC", alpha=0.35)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(temp.name, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return temp.name

# ----------------------------------------------------------
# PAGE HEADER / FOOTER
# ----------------------------------------------------------
def draw_header_footer(c: canvas.Canvas, title: str, page: int, logo_path: str):
    width, height = A4

    # Header
    c.setFillColor(colors.HexColor(HEADER_COLOR))
    c.rect(0, height - 70, width, 70, fill=1, stroke=0)

    # Title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(30, height - 45, title)

    # Logo
    if os.path.isfile(logo_path):
        try:
            img = ImageReader(logo_path)
            c.drawImage(img, width - 110, height - 65, width=70, preserveAspectRatio=True)
        except Exception:
            pass

    # Footer
    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica", 9)
    c.drawString(30, 25, "www.tlogic.consulting")
    c.drawCentredString(width / 2, 25, "T-Logic Consulting Pvt. Ltd.")
    c.drawRightString(width - 30, 25, str(page))


# ----------------------------------------------------------
# COLOR FOR DIMENSIONS
# ----------------------------------------------------------
def dim_color(name: str) -> str:
    return PASTEL_COLORS.get(name, "#DDDDDD")


# ----------------------------------------------------------
# READINESS LOOKUP
# ----------------------------------------------------------
def lookup_readiness(total: float):
    for r in READINESS_LEVELS:
        if r["min"] <= total <= r["max"]:
            return r
    return READINESS_LEVELS[0]


# ----------------------------------------------------------
# MAIN PDF GENERATOR
# ----------------------------------------------------------
def generate_pdf_report(results: Dict[str, Any], logo_path: str = "/static/TLogic_Logo4.png") -> bytes:
    try:
        # Unpack user scores
        overall = results["overall_score"]
        dim_scores = results["dimension_scores"]  # dict of 6 dims, each 1–5
        exec_summary = results.get("summary", "Your current processes are showing good traction...")
        recs = results.get("recommendations", {})

        readiness = lookup_readiness(overall)

        # radar chart
        radar_path = generate_radar_chart(dim_scores)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # -----------------------------------------------------
        # PAGE 1
        # -----------------------------------------------------
        draw_header_footer(c, "AI-Enabled Readiness Assessment", 1, logo_path)

        # Overall readiness box row (mock-up)
        c.setFont("Helvetica", 10)

        # Left box
        c.rect(30, height - 180, 150, 70)
        c.drawCentredString(105, height - 150, f"Overall Readiness")
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(105, height - 170, f"{overall:.1f}/30")

        # Middle
        c.setFont("Helvetica", 10)
        c.rect(190, height - 180, 150, 70)
        c.drawCentredString(265, height - 150, "Readiness %")
        c.setFont("Helvetica-Bold", 16)
        pct = (overall / 30) * 100
        c.drawCentredString(265, height - 170, f"{pct:.0f}%")

        # Right
        c.setFont("Helvetica", 10)
        c.rect(350, height - 180, 200, 70)
        c.drawCentredString(450, height - 150, "Indicates:")
        c.setFillColor(colors.HexColor(readiness["color"]))
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(450, height - 170, readiness["label"])
        c.setFillColor(colors.black)

        # Executive Summary box
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, height - 210, "Executive Summary:")
        c.setFont("Helvetica", 10)
        c.rect(30, height - 420, width - 60, 190)
        text = c.beginText(40, height - 240)
        text.setFont("Helvetica", 10)
        for line in exec_summary.split("\n"):
            text.textLine(line)
        c.drawText(text)

        # Scoring Model heading
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, height - 440, "Scoring Model")

        # Radar Chart
        c.drawImage(radar_path, 30, height - 780, width=250, preserveAspectRatio=True)

        c.showPage()

        # -----------------------------------------------------
        # PAGE 2
        # -----------------------------------------------------
        draw_header_footer(c, "AI-Enabled Readiness Assessment", 2, logo_path)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, height - 110, "Dimension Breakdown")

        y = height - 150

        # For each dimension, add bar
        for dim, score in dim_scores.items():
            pct = score / 5
            bar_width = (width - 200) * pct

            c.setFont("Helvetica", 10)
            c.drawString(30, y + 5, f"{dim} — {score:.1f}/5")

            # background
            c.setFillColor(colors.HexColor("#EEEEEE"))
            c.rect(200, y, width - 250, 18, fill=1, stroke=0)

            # colored bar
            c.setFillColor(colors.HexColor(dim_color(dim)))
            c.rect(200, y, bar_width, 18, fill=1, stroke=0)

            y -= 40

        # Benchmark comparison heading
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawString(30, y - 20, "Industry Benchmark Comparison:")

        # Bar chart: dynamic
        fig = plt.figure(figsize=(5.5, 2.8), facecolor="white")
        ax = fig.add_subplot(111)

        dims = list(dim_scores.keys())
        user_vals = [dim_scores[d] for d in dims]
        baseline_vals = [BASELINE_AVG[d] for d in dims]

        x = np.arange(len(dims))
        ax.bar(x - 0.2, user_vals, width=0.4, color="#003B73", label="Your Score")
        ax.bar(x + 0.2, baseline_vals, width=0.4, color="#888888", label="Benchmark")

        ax.set_xticks(x)
        ax.set_xticklabels(dims, rotation=30, ha="right")
        ax.set_ylim(0, 5)
        ax.legend()

        temp_bar = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig.savefig(temp_bar.name, dpi=150, bbox_inches="tight")
        plt.close(fig)

        c.drawImage(temp_bar.name, 30, y - 240, width - 60, preserveAspectRatio=True)

        c.showPage()

        # -----------------------------------------------------
        # PAGE 3
        # -----------------------------------------------------
        draw_header_footer(c, "AI-Enabled Readiness Assessment", 3, logo_path)

        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, height - 120, "Recommended Actions:")

        c.setFont("Helvetica", 10)
        text = c.beginText(40, height - 150)

        for dim, items in recs.items():
            text.textLine(f"• {dim}:")
            for rec in items:
                text.textLine(f"   - {rec}")
            text.textLine("")

        c.drawText(text)

        c.showPage()

        # Finish
        c.save()
        return buffer.getvalue()

    except Exception as e:
        print("PDF ERROR:", e)
        return b""
