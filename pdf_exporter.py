import json
from datetime import datetime
from pathlib import Path
from fpdf import FPDF
import io

class ReportPDF(FPDF):
    def __init__(self, title, subtitle):
        super().__init__()
        self.doc_title = title
        self.doc_subtitle = subtitle
        self.set_margins(15, 20, 15)
        self.add_page()
        
    def header(self):
        self.set_font("helvetica", "B", 20)
        self.set_text_color(15, 23, 42) # slate-900
        self.cell(0, 10, self.doc_title, new_x="LMARGIN", new_y="NEXT", align="L")
        
        self.set_font("helvetica", "", 12)
        self.set_text_color(100, 116, 139) # slate-500
        self.cell(0, 8, self.doc_subtitle, new_x="LMARGIN", new_y="NEXT", align="L")
        
        self.set_draw_color(226, 232, 240) # slate-200
        self.line(15, self.get_y()+2, 195, self.get_y()+2)
        self.set_y(self.get_y() + 10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184) # slate-400
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.cell(0, 10, f"Generated automatically by RuleCheck | {ts} | Page {self.page_no()}", align="C")

def export_rules_pdf(rules: list[dict]) -> bytes:
    pdf = ReportPDF("Policy Rules Database", "Extracted automated enforcement logic")
    pdf.set_font("helvetica", "", 10)
    
    for idx, rule in enumerate(rules, 1):
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(30, 64, 175) # blue-800
        pdf.cell(0, 8, f"{rule.get('id', f'RULE_{idx}')} - {rule.get('rule_type', 'Policy').title()}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(51, 65, 85) # slate-700
        pdf.multi_cell(0, 6, f"Description: {rule.get('description', '')}")
        pdf.multi_cell(0, 6, f"Condition: {rule.get('condition_field', '')} {rule.get('operator', '')} {rule.get('threshold_value', '')}")
        
        pdf.set_font("courier", "", 9)
        pdf.set_text_color(71, 85, 105) # slate-600
        pdf.multi_cell(0, 5, f"SQL: {rule.get('sql_hint', '')}")
        
        pdf.set_y(pdf.get_y() + 6)
        
    return bytes(pdf.output(dest="S"))

def export_violations_pdf(violations: list[dict]) -> bytes:
    pdf = ReportPDF("Violation Analysis Report", "Comprehensive view of triggered compliance rules")
    
    for v in sorted(violations, key=lambda x: x.get("violation_count", 0), reverse=True):
        count = v.get("violation_count", 0)
        if count == 0: continue
            
        pdf.set_font("helvetica", "B", 12)
        if count >= 500:
            pdf.set_text_color(185, 28, 28) # red-700
        elif count >= 50:
            pdf.set_text_color(180, 83, 9) # amber-700
        else:
            pdf.set_text_color(21, 128, 61) # green-700
            
        pdf.cell(0, 8, f"{v.get('rule_id', '?')} - {count:,} Violations", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 6, f"Description: {v.get('rule_description', '')}")
        
        if v.get('sample_violations'):
            pdf.set_y(pdf.get_y() + 2)
            pdf.set_font("helvetica", "B", 9)
            pdf.cell(0, 6, "Sample Trace:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("courier", "", 8)
            pdf.set_text_color(100, 116, 139)
            pdf.multi_cell(0, 4, json.dumps(v.get('sample_violations')[:1], indent=2))
        
        pdf.set_y(pdf.get_y() + 8)
        
    return bytes(pdf.output(dest="S"))

def export_explanations_pdf(explanations: list[dict]) -> bytes:
    pdf = ReportPDF("AI Risk Analysis & Explanations", "Contextualized human-readable insights mapping")
    
    for ex in sorted(explanations, key=lambda x: x.get("violation_count", 0), reverse=True):
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(0, 8, ex.get("alert_headline", "Alert"))
        
        pdf.set_font("helvetica", "B", 10)
        risk = ex.get("risk_level", "UNKNOWN")
        if "HIGH" in risk: pdf.set_text_color(220, 38, 38)
        elif "MEDIUM" in risk: pdf.set_text_color(217, 119, 6)
        else: pdf.set_text_color(22, 163, 74)
        pdf.cell(0, 6, f"Risk Level: {risk} | Rule ID: {ex.get('rule_id', '?')}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)
        pdf.set_y(pdf.get_y() + 2)
        pdf.multi_cell(0, 6, ex.get("plain_english", ""))
        
        pdf.set_y(pdf.get_y() + 2)
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(0, 6, f"Recommended Action: {ex.get('recommended_action', '')}")
        
        pdf.set_y(pdf.get_y() + 8)
        
    return bytes(pdf.output(dest="S"))

def export_compliance_report(rules, violations, explanations, hitl_decisions) -> bytes:
    """Master report combining everything + HITL decisions"""
    pdf = ReportPDF("Master Compliance Audit Report", "End-to-end trace of policy to automated enforcement")
    
    # Exec Summary
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, "Executive Summary", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(51, 65, 85)
    total_r = len(rules)
    triggered = sum(1 for v in violations if v.get("violation_count", 0) > 0)
    total_v = sum(v.get("violation_count", 0) for v in violations)
    reviewed = len(hitl_decisions)
    
    summary = (
        f"This audit validates the automated extraction and execution of {total_r} compliance rules. "
        f"Out of the deployed policies, {triggered} rules were triggered resulting in {total_v:,} distinct transaction violations. "
        f"Human-in-the-Loop compliance officers have reviewed {reviewed} critical alerts."
    )
    pdf.multi_cell(0, 6, summary)
    pdf.set_y(pdf.get_y() + 10)
    
    # Rule Breakdown
    for ex in sorted(explanations, key=lambda x: x.get("violation_count", 0), reverse=True):
        rid = ex.get("rule_id", "?")
        decision = hitl_decisions.get(rid, {}).get("action", "PENDING")
        
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(0, 8, f"[{rid}] {ex.get('risk_level', '')} Risk ({ex.get('violation_count', 0):,} hits)", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 6, ex.get("alert_headline", ""))
        
        # Decision box
        pdf.set_font("helvetica", "B", 9)
        if decision == "CONFIRMED": pdf.set_text_color(22, 163, 74)
        elif decision == "ESCALATED": pdf.set_text_color(220, 38, 38)
        elif decision == "DISMISSED": pdf.set_text_color(100, 116, 139)
        else: pdf.set_text_color(217, 119, 6)
        
        pdf.cell(0, 6, f"> Analyst Decision: {decision}", new_x="LMARGIN", new_y="NEXT")
        
        notes = hitl_decisions.get(rid, {}).get("notes", "")
        if notes:
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(100, 116, 139)
            pdf.multi_cell(0, 5, f"Notes: {notes}")
            
        pdf.set_y(pdf.get_y() + 6)
        
    return bytes(pdf.output(dest="S"))
