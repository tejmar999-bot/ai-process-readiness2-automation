# utils/pdf_generator.py

from fpdf import FPDF
import datetime
import os
from typing import Any, Dict


def _ensure_text(s: Any) -> str:
    if s is None:
        return ""
    if isinstance(s, (list, tuple)):
        return "\n".join(str(x) for x in s)
    return str(s)


def generate_pdf_report(results: Dict[str, Any], font_path: str = None) -> bytes:
    """
    Generate a compact PDF report for AI-Enabled Process Readiness.
    Returns bytes usable by Streamlit's download_button or tests.
    """
    try:
        pdf = FPDF(format="A4")
        left_margin = 15
        right_margin = 15
        top_margin = 15
        pdf.set_left_margin(left_margin)
        pdf.set_right_margin(right_margin)
        pdf.set_top_margin(top_margin)
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.add_page()

        # Register DejaVu font if provided (unicode-capable)
        use_dejavu = False
        if font_path and os.path.isfile(font_path):
            try:
                pdf.add_font("DejaVu", "", font_path, uni=True)
                pdf.add_font("DejaVu", "B", font_path, uni=True)
                use_dejavu = True
            except Exception:
                use_dejavu = False

        def set_font_b(size=12, bold=False):
            family = "DejaVu" if use_dejavu else "Arial"
            style = "B" if bold else ""
            pdf.set_font(family, style, size)

        # Header
        set_font_b(size=14, bold=True)
        pdf.cell(0, 10, txt="AI-Enabled Process Readiness Report", ln=True, align="C")
        pdf.ln(3)

        # Meta
        set_font_b(size=9, bold=False)
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        pdf.cell(0, 6, txt=f"Generated on: {timestamp}", ln=True, align="L")
        pdf.ln(3)

        # Overall score
        overall = results.get("overall_score", 0.0)
        set_font_b(size=12, bold=True)
        pdf.cell(0, 7, txt=f"Overall Readiness: {overall:.2f} / 5", ln=True)
        pdf.ln(2)

        # Dimension scores
        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, txt="Dimension scores:", ln=True)
        set_font_b(size=10, bold=False)
        dims = results.get("dimensions", [])
        scores = results.get("dimension_scores", [])
        for name, score in zip(dims, scores):
            pdf.multi_cell(0, 6, txt=f"- {name}: {score:.2f} / 5")
        pdf.ln(3)

        # Recommendations / notes
        notes_raw = results.get("notes") or results.get("recommendations") or ""
        notes = _ensure_text(notes_raw).strip()
        if notes:
            set_font_b(size=11, bold=True)
            pdf.cell(0, 6, txt="Recommendations:", ln=True)
            set_font_b(size=10, bold=False)
            pdf.multi_cell(0, 6, txt=notes)
            pdf.ln(3)

        # Footer / disclaimer
        set_font_b(size=9, bold=False)
        disclaimer = (
            "This report provides a high-level readiness overview based on subjective inputs. "
            "It should not be interpreted as a comprehensive professional evaluation."
        )
        pdf.multi_cell(0, 6, txt=disclaimer)

        # Produce PDF as string then convert to bytes (safe for different fpdf builds)
        out = pdf.output(dest="S")
        if isinstance(out, str):
            try:
                return out.encode("latin-1")
            except Exception:
                return out.encode("utf-8", errors="ignore")
        else:
            return bytes(out)

    except Exception as e:
        # If something goes wrong, return a small PDF with the error message so you can download and inspect it
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 6, txt=f"PDF generation error: {str(e)}")
            out = pdf.output(dest="S")
            if isinstance(out, str):
                return out.encode("latin-1", errors="ignore")
            return bytes(out)
        except Exception:
            # final fallback: return a minimal PDF header as bytes
            return b"%PDF-1.4\n%PDF-fallback\n"
