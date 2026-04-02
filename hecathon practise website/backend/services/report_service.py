from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from typing import List, Dict, Any
from datetime import datetime
import os

class ReportService:
    """
    Expert-level service for generating structured, authority-ready PDF compliance reports.
    """
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except:
                pass

    def generate_pdf(self, tile_id: str, detection_results: List[Dict[str, Any]], violations: List[Dict[str, Any]], area_name: str = "Unnamed Zone") -> str:
        """
        Creates a high-fidelity PDF report using Platypus engine.
        """
        report_filename = f"GeoWatch_Compliance_Audit_{tile_id}.pdf"
        report_path = os.path.join(self.output_dir, report_filename)
        
        doc = SimpleDocTemplate(report_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor("#0f172a"), spaceAfter=12)
        subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor("#64748b"), spaceAfter=20)
        section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor("#1e293b"), spaceBefore=15, spaceAfter=10)
        
        elements = []
        
        # 1. HEADER
        elements.append(Paragraph(f"GeoWatch AI Audit: {area_name}", title_style))
        elements.append(Paragraph(f"Zone ID: {tile_id} | Official report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        elements.append(Spacer(1, 12))
        
        # 2. EXECUTIVE SUMMARY
        elements.append(Paragraph("1. Executive Summary", section_style))
        
        # Categorize results
        deforestation = [d for d in detection_results if d.get('label') == "Deforestation"]
        water_loss = [d for d in detection_results if d.get('label') == "Water Body Loss"]
        road_expansion = [d for d in detection_results if d.get('label') == "Road Expansion"]
        illegal_const = [d for d in detection_results if d.get('label') == "Illegal Construction"]
        authorized = [d for d in detection_results if d.get('label') == "Authorized Development"]
        
        summary_intro = f"This report covers environmental and structural change detection for inspection zone <b>{area_name}</b>. The AI engine has analyzed multi-temporal satellite imagery to identify land-use transitions."
        elements.append(Paragraph(summary_intro, styles['Normal']))
        elements.append(Spacer(1, 10))

        # Impact Breakdown
        impact_data = [
            [Paragraph("🌳 Deforestation", styles['Normal']), f"{len(deforestation)} instances", f"{sum(d.get('area_sqm', 0) for d in deforestation):.1f} sqm"],
            [Paragraph("💧 Water Body Loss", styles['Normal']), f"{len(water_loss)} instances", f"{sum(d.get('area_sqm', 0) for d in water_loss):.1f} sqm"],
            [Paragraph("🛣️ Road Expansion", styles['Normal']), f"{len(road_expansion)} instances", f"{sum(d.get('area_sqm', 0) for d in road_expansion):.1f} sqm"],
            [Paragraph("🏗️ Illegal Construction", styles['Normal']), f"{len(illegal_const)} instances", f"{sum(d.get('area_sqm', 0) for d in illegal_const):.1f} sqm"]
        ]
        
        impact_table = Table(impact_data, colWidths=[180, 100, 100])
        impact_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ]))
        elements.append(impact_table)
        elements.append(Spacer(1, 12))
        
        # 3. DETECTION LOG TABLE
        elements.append(Paragraph("2. Detailed Detection Logs", section_style))
        
        if not detection_results:
            elements.append(Paragraph("<i>No significant changes detected in this analysis cycle.</i>", styles['Normal']))
        else:
            # Table Data with explicit categorization
            data = [["Category", "Area (sqm)", "Confidence", "Status"]]
            row_styles = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]
            
            for idx, res in enumerate(detection_results):
                label = res.get('label', 'Modification')
                is_violation = label != "Authorized Development"
                
                # Determine Color Coding
                row_color = colors.white
                if label == "Deforestation": row_color = colors.HexColor("#fef2f2") # Light red
                elif label == "Water Body Loss": row_color = colors.HexColor("#eff6ff") # Light blue
                elif label == "Road Expansion": row_color = colors.HexColor("#fffbeb") # Light yellow
                elif label == "Authorized Development": row_color = colors.HexColor("#f0fdf4") # Light green
                
                data.append([
                    label,
                    f"{res.get('area_sqm', 0):.2f}",
                    f"{res.get('confidence', 0)*100:.1f}%",
                    "VIOLATION" if is_violation else "AUTHORIZED"
                ])
                
                row_styles.append(('BACKGROUND', (0, idx+1), (-1, idx+1), row_color))
                if is_violation:
                    row_styles.append(('TEXTCOLOR', (3, idx+1), (3, idx+1), colors.red))
            
            t = Table(data, colWidths=[150, 100, 100, 120])
            t.setStyle(TableStyle(row_styles))
            elements.append(t)
        
        # 4. VIOLATIONS & LEGAL ACTION
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("3. Statutory Zoning Compliance (AUDA)", section_style))
        
        if not violations:
            elements.append(Paragraph("<b>COMPLIANCE NOTICE:</b> Area is fully compliant with local zoning regulations.", styles['Normal']))
        else:
            for v in violations:
                v_type = v.get('type', 'General Violation')
                severity = v.get('severity', 'High')
                reason = v.get('reason', 'N/A')
                
                v_text = f"<b>FLAGGED:</b> {v_type} (Severity: {severity})<br/>" \
                         f"<b>Founding Reason:</b> {reason}"
                elements.append(Paragraph(v_text, styles['Normal']))
                elements.append(Spacer(1, 6))

        # 5. FOOTER / LEGAL
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("This document is generated by the GeoWatch AI Engine and is intended for official use by development authorities only. Unauthorized changes to land-use are subject to municipal penalties.", styles['Italic']))
        
        # Build PDF
        doc.build(elements)
        return report_path

# Example:
# svc = ReportService()
# svc.generate_pdf("tile_test", "Detected construction in rural area.", [{"type": "Unapproved Structure", "status": "Violation", "severity": "High", "reason": "No permits found for this area."}])
