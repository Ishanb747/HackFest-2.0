"""
generate_test_pdf.py — Creates a synthetic AML policy PDF for testing Turgon.
Run once: python generate_test_pdf.py
"""
from fpdf import FPDF
from pathlib import Path


class PolicyPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(15, 30, 60)
        self.set_text_color(255, 255, 255)
        self.cell(
            0, 12,
            "ANTI-MONEY LAUNDERING COMPLIANCE POLICY",
            align="C", fill=True, new_x="LMARGIN", new_y="NEXT",
        )
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Turgon Test Policy v1.0  |  Page {self.page_no()}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(225, 232, 248)
        self.cell(0, 8, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def rule_block(self, rule_id: str, rule_text: str):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(170, 30, 30)
        self.cell(0, 6, rule_id, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, rule_text)
        self.ln(3)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(2)


def build_pdf(out_path: Path) -> None:
    pdf = PolicyPDF()
    pdf.set_margins(18, 18, 18)
    pdf.add_page()

    # ── Preamble ─────────────────────────────────────────────────────────────
    pdf.body_text(
        "This policy document establishes mandatory compliance rules for financial "
        "institutions under FinCEN guidance and FATF Recommendation 16 (Wire Transfer "
        "Rule). All automated monitoring systems must enforce the following thresholds "
        "and conditions without exception. Effective date: 2024-01-01."
    )

    # ── Section 1: Transaction Threshold Rules ────────────────────────────────
    pdf.section_title("SECTION 1 -- TRANSACTION THRESHOLD REPORTING RULES")

    pdf.rule_block(
        "RULE 1.1 -- Currency Transaction Report (CTR)",
        "Any cash transaction or series of related cash transactions that exceeds "
        "USD 10,000 in a single business day MUST be reported to FinCEN within 15 "
        "calendar days. Condition: Amount_Paid > 10000 AND Payment_Format = 'Cash'.",
    )
    pdf.rule_block(
        "RULE 1.2 -- Large Wire Transfer Monitoring",
        "All wire transfers where the Amount_Paid exceeds USD 50,000 in a single "
        "transaction must be flagged for enhanced due diligence. The originating bank "
        "and account must be verified against the OFAC SDN list. "
        "Condition: Amount_Paid > 50000 AND Payment_Format = 'Wire'.",
    )
    pdf.rule_block(
        "RULE 1.3 -- Structuring / Smurfing Detection",
        "Accounts that conduct more than 5 separate transactions within a 24-hour "
        "period, each individually below USD 10,000 but cumulatively exceeding USD "
        "10,000, are suspected of structuring. Flag accounts where total daily outflow "
        "> 10000 and individual transactions < 10000.",
    )
    pdf.rule_block(
        "RULE 1.4 -- High-Value Reinvestment Transactions",
        "Any transaction classified as Payment_Format = 'Reinvestment' where the "
        "Amount_Paid exceeds USD 25,000 must be escalated to the compliance officer "
        "for manual review within 48 hours. "
        "Condition: Amount_Paid > 25000 AND Payment_Format = 'Reinvestment'.",
    )

    # ── Section 2: Cross-Border & Currency Rules ──────────────────────────────
    pdf.add_page()
    pdf.section_title("SECTION 2 -- CROSS-BORDER AND CURRENCY RULES")

    pdf.rule_block(
        "RULE 2.1 -- Currency Conversion Mismatch Alert",
        "Any transaction where the Payment_Currency differs from the "
        "Receiving_Currency and the Amount_Paid exceeds USD 5,000 must be logged as "
        "a potential layering event. "
        "Condition: Payment_Currency != Receiving_Currency AND Amount_Paid > 5000.",
    )
    pdf.rule_block(
        "RULE 2.2 -- High-Risk Jurisdiction Transfers",
        "Transfers originating from or destined to banks in high-risk jurisdictions "
        "where the amount exceeds USD 1,000 must be automatically flagged pending "
        "review. Condition: Amount_Paid > 1000 (apply jurisdiction filter at runtime).",
    )
    pdf.rule_block(
        "RULE 2.3 -- Rapid Cross-Currency Round-Trip",
        "Transactions where the Amount_Received deviates by more than 15 percent "
        "from Amount_Paid (after FX normalisation) may indicate layering. "
        "Flag all mismatches where Amount_Paid > 2000.",
    )

    # ── Section 3: Account Behaviour Rules ───────────────────────────────────
    pdf.section_title("SECTION 3 -- ACCOUNT BEHAVIOUR MONITORING RULES")

    pdf.rule_block(
        "RULE 3.1 -- Dormant Account Sudden Activity",
        "Accounts with no transactions for 90 or more days that suddenly initiate a "
        "transaction exceeding USD 5,000 must be flagged for review. "
        "Condition: Amount_Paid > 5000 (dormancy check requires temporal analysis).",
    )
    pdf.rule_block(
        "RULE 3.2 -- Round-Number Transaction Pattern",
        "Transactions where Amount_Paid is an exact multiple of 1000 and Amount_Paid "
        ">= 5000 are statistically overrepresented in confirmed laundering cases. "
        "Condition: Amount_Paid >= 5000 AND Amount_Paid % 1000 = 0.",
    )

    # ── Section 4: Payment Format Rules ──────────────────────────────────────
    pdf.add_page()
    pdf.section_title("SECTION 4 -- PAYMENT FORMAT SPECIFIC RULES")

    pdf.rule_block(
        "RULE 4.1 -- Cheque Transactions Above Threshold",
        "Any cheque-based payment exceeding USD 15,000 must be verified against the "
        "account holder identity. "
        "Condition: Amount_Paid > 15000 AND Payment_Format = 'Cheque'.",
    )
    pdf.rule_block(
        "RULE 4.2 -- Credit Card Large Purchases",
        "Credit card transactions exceeding USD 8,000 in a single transaction must "
        "be reviewed for potential card-not-present fraud. "
        "Condition: Amount_Paid > 8000 AND Payment_Format = 'Credit Card'.",
    )
    pdf.rule_block(
        "RULE 4.3 -- ACH High-Value Transfers",
        "ACH transfers from a single account totalling more than USD 100,000 within "
        "a 7-day period constitute a high-risk aggregation pattern. "
        "Condition: Payment_Format = 'ACH' AND Amount_Paid > 10000.",
    )

    # ── Section 5: Confirmed Laundering Baseline ──────────────────────────────
    pdf.section_title("SECTION 5 -- CONFIRMED LAUNDERING BASELINE CHECKS")

    pdf.rule_block(
        "RULE 5.1 -- Known Laundering Transaction Audit",
        "All transactions where Is_Laundering = 1 must appear in the quarterly audit "
        "report. This rule validates the detection system is operating correctly. "
        "Condition: Is_Laundering = 1.",
    )
    pdf.rule_block(
        "RULE 5.2 -- High-Value Confirmed Laundering",
        "Confirmed laundering transactions where Amount_Paid exceeds USD 50,000 "
        "require immediate escalation to the Financial Intelligence Unit (FIU). "
        "Condition: Is_Laundering = 1 AND Amount_Paid > 50000.",
    )

    # ── Disclaimer ────────────────────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(110, 110, 110)
    pdf.multi_cell(
        0, 5,
        "This document is a synthetic test policy generated for the Turgon compliance "
        "engine. All thresholds referenced are consistent with FinCEN guidance 2024 "
        "and FATF Recommendation 16. For production use, consult your legal team.",
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    print(f"PDF saved:  {out_path}")
    print(f"Pages:      {pdf.page}")
    print(f"File size:  {out_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    out = Path(r"D:\Projects\Hackfest 2.0\turgon\uploads\test_aml_policy.pdf")
    build_pdf(out)
