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


def generate_pdf_report(results: Dict[str, Any], company_name: str = None, primary_color: str = None, logo_image = None, font_path: str = None) -> bytes:
    """
    Generate a comprehensive PDF report for AI-Enabled Process Readiness.
    Returns bytes usable by Streamlit's download_button or tests.
    
    Args:
        results: Dictionary containing assessment scores and data
        company_name: Name of the company (optional)
        primary_color: Primary color for branding (optional)
        logo_image: Company logo image (optional)
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
        set_font_b(size=16, bold=True)
        title_text = "AI Process Readiness Assessment"
        if company_name:
            title_text = f"{company_name}\n{title_text}"
        pdf.multi_cell(0, 8, title_text, align="C")
        pdf.ln(4)

        # Meta
        set_font_b(size=9, bold=False)
        timestamp = datetime.datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
        pdf.cell(0, 6, f"Report Generated: {timestamp}", ln=True, align="L")
        pdf.ln(3)

        # Overall score section
        total_score = results.get("total", 0.0)
        percentage = results.get("percentage", 0)
        readiness_band = results.get("readiness_band", {})
        
        set_font_b(size=11, bold=True)
        pdf.cell(0, 7, f"Overall Score: {total_score:.1f} / 30 ({percentage}%)", ln=True)
        
        # Readiness level with color indication
        band_label = readiness_band.get("label", "N/A")
        band_desc = readiness_band.get("description", "")
        set_font_b(size=10, bold=True)
        pdf.cell(0, 6, f"Readiness Level: {band_label}", ln=True)
        if band_desc:
            set_font_b(size=9, bold=False)
            pdf.multi_cell(0, 5, band_desc)
        pdf.ln(3)

        # Executive Summary
        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, "Executive Summary", ln=True)
        pdf.ln(1)
        set_font_b(size=9, bold=False)
        
        # Generate dynamic executive summary based on scores
        dimension_scores = results.get("dimension_scores", [])
        from data.dimensions import DIMENSIONS
        
        # Handle both numeric and dict formats for dimension_scores
        lowest_dims = []
        for i, score_data in enumerate(dimension_scores):
            if isinstance(score_data, dict):
                score_value = score_data.get('score', 0)
            else:
                score_value = score_data
            lowest_dims.append((i, score_value))
        
        lowest_dims = sorted(lowest_dims, key=lambda x: x[1])[:2]
        lowest_names = [DIMENSIONS[i]['title'] for i, _ in lowest_dims]
        
        if percentage < 40:
            summary = f"This organization is in the foundational stage of AI readiness. Current score of {total_score:.1f}/30 indicates significant work is needed to establish core capabilities. Key focus areas include {lowest_names[0]} and {lowest_names[1]}. Building strong foundational processes and infrastructure is essential before advanced AI initiatives can be successfully implemented. Recommend starting with pilot projects to build organizational confidence and capability."
        elif percentage < 60:
            summary = f"This organization shows emerging AI readiness with a score of {total_score:.1f}/30. While progress has been made, important gaps remain in {lowest_names[0]} and {lowest_names[1]}. Establishing clear governance, building technical infrastructure, and developing team capabilities should be prioritized. A structured roadmap with phased implementation will help accelerate progress toward operational AI integration."
        elif percentage < 80:
            summary = f"This organization demonstrates reliable AI readiness with a score of {total_score:.1f}/30. Most foundational elements are in place for successful AI initiatives. Fine-tuning capabilities in {lowest_names[0]} and {lowest_names[1]} will unlock greater operational value. Focus should shift toward scaling successful pilots and establishing centers of excellence for broader organizational adoption."
        else:
            summary = f"This organization demonstrates exceptional AI readiness with a score of {total_score:.1f}/30. Strong foundational capabilities across processes, technology, data, people, leadership, and governance enable advanced AI implementation. Continue optimizing and scaling current initiatives while exploring innovative use cases. Consider sharing best practices and thought leadership with the industry."
        
        pdf.multi_cell(0, 5, summary)
        pdf.ln(2)

        # Dimension Breakdown
        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, "Dimension Breakdown", ln=True)
        pdf.ln(2)
        
        # Create dimension breakdown chart data in text format
        for i, score_data in enumerate(dimension_scores):
            if i < len(DIMENSIONS):
                dim = DIMENSIONS[i]
                dim_name = dim['title']
                # Handle both numeric and dict formats for dimension_scores
                if isinstance(score_data, dict):
                    dim_score = score_data.get('score', 0)
                else:
                    dim_score = score_data
                percentage_score = (dim_score / 5) * 100
                
                # Dimension name and score
                set_font_b(size=10, bold=True)
                pdf.cell(0, 6, f"{i+1}. {dim_name}: {dim_score:.1f}/5 ({percentage_score:.0f}%)", ln=True)
        
        pdf.ln(2)

        # Recommendations based on lowest scoring dimensions
        set_font_b(size=11, bold=True)
        pdf.cell(0, 6, "Key Recommendations", ln=True)
        pdf.ln(1)
        set_font_b(size=9, bold=False)
        
        # Get 3-4 lowest scoring dimensions for recommendations
        scored_dims = []
        for i, score_data in enumerate(dimension_scores):
            if isinstance(score_data, dict):
                score_value = score_data.get('score', 0)
            else:
                score_value = score_data
            scored_dims.append((i, score_value, DIMENSIONS[i]['title']))
        scored_dims.sort(key=lambda x: x[1])
        lowest_count = min(4, len(scored_dims))
        
        recommendations = []
        
        # Add dimension-specific recommendations
        for i in range(lowest_count):
            idx, score, name = scored_dims[i]
            if score < 3.0:
                if name == "Process Maturity":
                    recommendations.append(f"- {name} ({score:.1f}/5): Develop and document standardized processes. Implement performance metrics and tracking systems.")
                elif name == "Technology Infrastructure":
                    recommendations.append(f"- {name} ({score:.1f}/5): Modernize technology stack and ensure systems are reliable. Invest in automation capabilities.")
                elif name == "Data Readiness":
                    recommendations.append(f"- {name} ({score:.1f}/5): Improve data accessibility and standardization. Ensure data quality across systems.")
                elif name == "People & Culture":
                    recommendations.append(f"- {name} ({score:.1f}/5): Invest in training and change management. Foster a culture of experimentation and continuous learning.")
                elif name == "Leadership & Alignment":
                    recommendations.append(f"- {name} ({score:.1f}/5): Secure leadership commitment and clearly communicate strategic priorities. Allocate sufficient resources for transformation.")
                elif name == "Governance & Risk":
                    recommendations.append(f"- {name} ({score:.1f}/5): Define clear roles and responsibilities. Establish risk management and compliance processes.")
            else:
                if name == "Process Maturity":
                    recommendations.append(f"- {name} ({score:.1f}/5): Maintain process discipline. Continuously improve through measurement and optimization.")
                elif name == "Technology Infrastructure":
                    recommendations.append(f"- {name} ({score:.1f}/5): Continue modernizing systems. Expand automation and integrate new tools.")
                elif name == "Data Readiness":
                    recommendations.append(f"- {name} ({score:.1f}/5): Advance data governance. Implement advanced analytics capabilities.")
                elif name == "People & Culture":
                    recommendations.append(f"- {name} ({score:.1f}/5): Deepen AI literacy. Build centers of excellence and expand innovation programs.")
                elif name == "Leadership & Alignment":
                    recommendations.append(f"- {name} ({score:.1f}/5): Reinforce strategic vision. Scale successful initiatives across the organization.")
                elif name == "Governance & Risk":
                    recommendations.append(f"- {name} ({score:.1f}/5): Strengthen governance frameworks. Expand compliance and risk monitoring.")
        
        for rec in recommendations:
            pdf.multi_cell(0, 5, rec)
        
        pdf.ln(2)

        # Footer / disclaimer
        set_font_b(size=8, bold=False)
        disclaimer = (
            "This report provides a high-level readiness overview based on subjective inputs. "
            "It should not be interpreted as a comprehensive professional evaluation. "
            "For detailed implementation guidance, consult with qualified AI transformation experts."
        )
        pdf.multi_cell(0, 4, disclaimer)

        # Produce PDF as string then convert to bytes (safe for different fpdf builds)
        out = pdf.output(dest="S")
        if isinstance(out, str):
            try:
                return out.encode("utf-8")
            except Exception:
                try:
                    return out.encode("latin-1", errors="ignore")
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
