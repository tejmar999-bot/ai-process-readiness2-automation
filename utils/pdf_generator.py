# utils/pdf_generator.py

from fpdf2 import FPDF
import datetime
import os
from typing import Any, Dict


def _ensure_text(s: Any) -> str:
    if s is None:
        return ""
    if isinstance(s, (list, tuple)):
        return "\n".join(str(x) for x in s)
    return str(s)


def generate_pdf_report(results: Dict[str, Any], company_name: str = None, primary_color: str = None, logo_image = None, font_path: str = None) -> bytes:
    """
    Generate a compact PDF report for AI-Enabled Process Readiness.
    Returns bytes usable by Streamlit's download_button or tests.
    
    Args:
        results: Dictionary containing assessment scores and data
        company_name: Name of the company (optional)
        primary_color: Primary color for branding (optional, not used yet)
        logo_image: Company logo image (optional, not used yet)
        font_path: Path to custom font file (optional)
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
        title_text = "AI-Enabled Process Readiness Report"
        if company_name:
            title_text = f"{company_name} - {title_text}"
        pdf.cell(0, 10, title_text, ln=True, align="C")
        pdf.ln(3)

        # Meta
        set_font_b(size=9, bold=False)
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        pdf.cell(0, 6, f"Generated on: {timestamp}", ln=True, align="L")
        pdf.ln(3)

        # Overall score (total out of 30)
        total_score = results.get("total", 0.0)
        percentage = results.get("percentage", 0)
        readiness_band = results.get("readiness_band", {})
        
        set_font_b(size=12, bold=True)
        pdf.cell(0, 7, f"Overall Score: {total_score:.1f} / 30 ({percentage}%)", ln=True)
        pdf.ln(2)
        
        # Readiness level
        band_label = readiness_band.get("label", "N/A")
        band_desc = readiness_band.get("description", "")
        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, f"Readiness Level: {band_label}", ln=True)
        if band_desc:
            set_font_b(size=9, bold=False)
            pdf.multi_cell(0, 5, str(band_desc))
        pdf.ln(3)

        # Dimension scores with details
        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, "Dimension Breakdown:", ln=True)
        pdf.ln(1)
        
        # Import dimensions to get names and descriptions
        from data.dimensions import DIMENSIONS
        dimension_scores = results.get("dimension_scores", [])
        
        for i, score_data in enumerate(dimension_scores):
            # Handle both dict format (new) and numeric format (old)
            if isinstance(score_data, dict):
                dim_name = score_data.get('title', '')
                dim_desc = score_data.get('description', '')
                score_value = score_data.get('score', 0.0)
            else:
                # Fallback to old format
                score_value = score_data
                if i < len(DIMENSIONS):
                    dim = DIMENSIONS[i]
                    dim_name = dim['title']
                    dim_desc = dim.get('description', '')
                else:
                    dim_name = f"Dimension {i+1}"
                    dim_desc = ""
            
            # Dimension title and score
            set_font_b(size=10, bold=True)
            pdf.multi_cell(0, 5, f"{i+1}. {dim_name}: {score_value:.1f} / 5")
            
            # Dimension description
            if dim_desc:
                set_font_b(size=9, bold=False)
                pdf.multi_cell(0, 4, f"   {str(dim_desc)}")
            
            pdf.ln(2)
        
        pdf.ln(1)

        # Recommendations based on scores
        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, "Key Recommendations:", ln=True)
        pdf.ln(1)
        set_font_b(size=9, bold=False)
        
        # Generate recommendations based on readiness band
        if percentage < 40:
            recs = [
                "Focus on building foundational capabilities across all dimensions",
                "Prioritize process documentation and data quality improvements",
                "Invest in leadership buy-in and strategic alignment",
                "Start with pilot projects to build organizational confidence"
            ]
        elif percentage < 60:
            recs = [
                "Address gaps in lower-scoring dimensions systematically",
                "Develop a clear AI roadmap aligned with business objectives",
                "Invest in team training and skill development",
                "Strengthen data governance and infrastructure"
            ]
        elif percentage < 80:
            recs = [
                "Fine-tune capabilities in lower-scoring areas",
                "Scale successful AI initiatives across the organization",
                "Establish centers of excellence for AI implementation",
                "Enhance change management and cultural adoption"
            ]
        else:
            recs = [
                "Maintain and optimize current AI capabilities",
                "Explore advanced AI use cases and innovations",
                "Share best practices across the organization",
                "Consider industry leadership and thought leadership opportunities"
            ]
        
        # Add custom recommendations for low-scoring dimensions
        for i, score_data in enumerate(dimension_scores):
            # Extract score value from dict or use directly
            if isinstance(score_data, dict):
                score_value = score_data.get('score', 0.0)
                dim_name = score_data.get('title', '')
            else:
                score_value = score_data
                dim_name = DIMENSIONS[i]['title'] if i < len(DIMENSIONS) else f"Dimension {i+1}"
            
            if score_value < 3.0:
                recs.append(f"Priority: Strengthen {dim_name} (current score: {score_value:.1f}/5)")
        
        for rec in recs:
            pdf.multi_cell(0, 5, f"  {rec}")
        
        pdf.ln(2)
        
        # Add any custom notes if provided
        notes_raw = results.get("notes") or results.get("recommendations") or ""
        notes = _ensure_text(notes_raw).strip()
        if notes:
            set_font_b(size=10, bold=True)
            pdf.cell(0, 6, "Additional Notes:", ln=True)
            set_font_b(size=9, bold=False)
            pdf.multi_cell(0, 5, str(notes))
            pdf.ln(2)

        # Footer / disclaimer
        set_font_b(size=9, bold=False)
        disclaimer = (
            "This report provides a high-level readiness overview based on subjective inputs. "
            "It should not be interpreted as a comprehensive professional evaluation."
        )
        pdf.multi_cell(0, 6, disclaimer)

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
            pdf.multi_cell(0, 6, f"PDF generation error: {str(e)}")
            out = pdf.output(dest="S")
            if isinstance(out, str):
                return out.encode("latin-1", errors="ignore")
            return bytes(out)
        except Exception:
            return b"%PDF-1.4\n%PDF-fallback\n"
