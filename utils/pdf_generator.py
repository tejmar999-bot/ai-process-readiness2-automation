from fpdf import FPDF
import datetime
import os
from typing import Any, Dict


def _ensure_text(s: Any) -> str:
    """Ensure the input is converted to a consistent string."""
    if s is None:
        return ""
    if isinstance(s, (list, tuple)):
        return "\n".join(str(x) for x in s)
    return str(s)


def generate_pdf_report(
    results: Dict[str, Any],
    company_name: str = None,
    primary_color: str = None,
    logo_image: str = None,
    font_path: str = None,
) -> bytes:
    """
    Generate a compact PDF report for AI-Enabled Process Readiness.
    Returns bytes usable by Streamlit's download_button.

    Args:
        results: Dictionary containing assessment scores and data.
        company_name: Optional branding.
        primary_color: Optional accent color (not used yet).
        logo_image: Optional logo (not used yet).
        font_path: Optional custom font path.
    """
    try:
        pdf = FPDF(format="A4")
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.add_page()

        # Optionally register a custom unicode font (DejaVu)
        use_unicode = False
        if font_path and os.path.isfile(font_path):
            try:
                pdf.add_font("DejaVu", "", font_path, uni=True)
                pdf.add_font("DejaVu", "B", font_path, uni=True)
                use_unicode = True
            except Exception:
                use_unicode = False

        def set_font_b(size=12, bold=False):
            family = "DejaVu" if use_unicode else "Arial"
            style = "B" if bold else ""
            pdf.set_font(family, style, size)

        # ---------- HEADER ----------
        set_font_b(size=14, bold=True)
        title = "AI-Enabled Process Readiness Report"
        if company_name:
            title = f"{company_name} – {title}"
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(3)

        # ---------- META ----------
        set_font_b(size=9)
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        pdf.cell(0, 6, f"Generated on: {timestamp}", ln=True)
        pdf.ln(2)

        # ---------- OVERALL SCORE ----------
        total_score = results.get("total", 0.0)
        percentage = results.get("percentage", 0)
        readiness_band = results.get("readiness_band", {})

        set_font_b(size=12, bold=True)
        pdf.cell(0, 7, f"Overall Score: {total_score:.1f} / 30 ({percentage}%)", ln=True)
        pdf.ln(2)

        # ---------- READINESS BAND ----------
        band_label = readiness_band.get("label", "N/A")
        band_desc = readiness_band.get("description", "")

        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, f"Readiness Level: {band_label}", ln=True)

        if band_desc:
            set_font_b(size=9)
            pdf.multi_cell(0, 5, band_desc)
        pdf.ln(3)

        # ---------- DIMENSION BREAKDOWN ----------
        from data.dimensions import DIMENSIONS  # safe to import inside function

        dimension_scores = results.get("dimension_scores", [])

        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, "Dimension Breakdown:", ln=True)
        pdf.ln(1)

        for i, score_data in enumerate(dimension_scores):
            # Modern dict format
            if isinstance(score_data, dict):
                dim_name = score_data.get("title", "")
                dim_desc = score_data.get("description", "")
                score_value = score_data.get("score", 0.0)
            else:
                # Legacy numeric fallback
                score_value = score_data
                if i < len(DIMENSIONS):
                    dim_name = DIMENSIONS[i]["title"]
                    dim_desc = DIMENSIONS[i].get("description", "")
                else:
                    dim_name = f"Dimension {i+1}"
                    dim_desc = ""

            # Title line
            set_font_b(size=10, bold=True)
            pdf.multi_cell(0, 5, f"{i+1}. {dim_name}: {score_value:.1f} / 5")

            # Description
            if dim_desc:
                set_font_b(size=9)
                pdf.multi_cell(0, 4, dim_desc)

            pdf.ln(2)

        # ---------- RECOMMENDATIONS ----------
        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, "Key Recommendations:", ln=True)
        pdf.ln(1)

        set_font_b(size=9)

        # Tier-based recs
        if percentage < 40:
            recs = [
                "Focus on foundational capabilities across all dimensions.",
                "Improve process documentation and data quality.",
                "Increase leadership buy-in and alignment.",
                "Start with small pilot initiatives.",
            ]
        elif percentage < 60:
            recs = [
                "Address systemic gaps in lower-scoring dimensions.",
                "Develop a clear organization-wide AI roadmap.",
                "Strengthen training and data governance.",
            ]
        elif percentage < 80:
            recs = [
                "Fine-tune capabilities in lower scoring areas.",
                "Scale successful AI initiatives.",
                "Enhance change management readiness.",
            ]
        else:
            recs = [
                "Maintain current maturity and optimize processes.",
                "Explore advanced AI use cases.",
                "Pursue thought-leadership opportunities.",
            ]

        # Add recs to PDF
        for r in recs:
            pdf.multi_cell(0, 5, f"• {r}")

        pdf.ln(3)

        # ---------- CUSTOM NOTES ----------
        notes = _ensure_text(results.get("notes") or results.get("recommendations")).strip()
        if notes:
            set_font_b(size=10, bold=True)
            pdf.cell(0, 6, "Additional Notes:", ln=True)
            set_font_b(size=9)
            pdf.multi_cell(0, 5, notes)
            pdf.ln(2)

        # ---------- FOOTER ----------
        disclaimer = (
            "This report provides a high-level readiness overview based on subjective inputs. "
            "It should not be interpreted as a comprehensive professional evaluation."
        )
        pdf.set_font("Arial", size=8)
        pdf.multi_cell(0, 4, disclaimer)

        # ---------- OUTPUT ----------
        out = pdf.output(dest="S")

        if isinstance(out, str):
            try:
                return out.encode("latin-1")
            except Exception:
                return out.encode("utf-8", errors="ignore")
        return bytes(out)

    except Exception as e:
        # Fallback PDF so user still gets something downloadable
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 6, f"PDF generation error: {str(e)}")
            out = pdf.output(dest="S")
            if isinstance(out, str):
                return out.encode("latin-1", errors="ignore")
            return bytes(out)
        except Exception:
            return b"%PDF-1.4\n%PDF-fallback\n"
