# PDF Export Feature Guide

## Overview

The RuleForge dashboard now supports exporting reports in professional PDF format alongside the existing JSON/CSV exports.

## Installation

To enable PDF export functionality, install the required library:

```bash
pip install reportlab
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## Available PDF Reports

### 1. Violation Report PDF (Tab 3: Violations)
- **Location:** Violations tab
- **Button:** "📄 Export Report (PDF)"
- **Contents:**
  - Executive summary with key metrics
  - Violations sorted by severity (HIGH/MEDIUM/LOW)
  - Color-coded severity indicators
  - Rule descriptions and violation counts
  - AI explanations (if Phase 3 was run)

### 2. Explanations PDF (Tab 4: AI Explanations)
- **Location:** AI Explanations tab
- **Button:** "📄 Export Explanations (PDF)"
- **Contents:**
  - All AI-generated explanations
  - Risk levels and recommended actions
  - Plain-English alerts
  - Policy references

### 3. Compliance Report PDF (Tab 5: Audit Log)
- **Location:** Audit Log tab
- **Button:** "📄 Download Report (PDF)"
- **Contents:**
  - Comprehensive compliance overview
  - Pipeline execution summary
  - Human-in-the-loop decision statistics
  - Audit log summary
  - Professional formatting for stakeholder review

## Features

✅ **Professional Formatting:** Clean, corporate-style layout  
✅ **Color-Coded Severity:** Visual indicators for HIGH/MEDIUM/LOW risks  
✅ **Automatic Timestamps:** Each report includes generation date/time  
✅ **Memory Efficient:** Generates PDFs on-demand without storing files  
✅ **Fallback Handling:** Graceful degradation if reportlab not installed  

## PDF Report Structure

### Violation Report
```
┌─────────────────────────────────────┐
│  ⚖️ RuleForge Violation Report      │
│  Generated: [timestamp]             │
├─────────────────────────────────────┤
│  Executive Summary                  │
│  • Total Rules Checked              │
│  • Rules Triggered                  │
│  • Total Violations                 │
│  • High Severity Rules              │
├─────────────────────────────────────┤
│  Violations by Severity             │
│  [HIGH] RULE_001 - 1,234 violations │
│  [MEDIUM] RULE_002 - 456 violations │
│  [LOW] RULE_003 - 78 violations     │
├─────────────────────────────────────┤
│  AI Explanations (if available)     │
│  • Plain-English alerts             │
│  • Recommended actions              │
└─────────────────────────────────────┘
```

### Compliance Report
```
┌─────────────────────────────────────┐
│  ⚖️ Compliance Report               │
│  Report Date: [timestamp]           │
├─────────────────────────────────────┤
│  Pipeline Summary                   │
│  • Rules Checked                    │
│  • Rules Triggered                  │
│  • Total Violations                 │
├─────────────────────────────────────┤
│  Human-in-the-Loop Decisions        │
│  • Confirmed                        │
│  • Dismissed                        │
│  • Escalated                        │
│  • Pending Review                   │
├─────────────────────────────────────┤
│  Audit Summary                      │
│  • Total Events                     │
│  • Pipeline Runs                    │
│  • HITL Decisions                   │
└─────────────────────────────────────┘
```

## Usage

1. Run the pipeline to generate violations
2. Navigate to the desired tab (Violations, Explanations, or Audit Log)
3. Click the "📄 Export Report (PDF)" button
4. The PDF will download automatically to your browser's download folder

## File Naming Convention

PDFs are automatically named with timestamps:
- `turgon_violation_report_YYYYMMDD_HHMM.pdf`
- `turgon_explanations_YYYYMMDD_HHMM.pdf`
- `turgon_compliance_report_YYYYMMDD_HHMM.pdf`

## Troubleshooting

### "Install reportlab to enable PDF export" warning
**Solution:** Run `pip install reportlab`

### PDF generation failed error
**Possible causes:**
- Insufficient disk space
- Permission issues in temp directory
- Corrupted data in violations/explanations

**Solution:** Check the error message for details and ensure you have write permissions

## Technical Details

- **Library:** ReportLab (open-source PDF generation)
- **Page Size:** US Letter (8.5" × 11")
- **Margins:** 0.75" (sides/bottom), 1" (top)
- **Colors:** RuleForge brand colors (#1d4ed8 primary)
- **Fonts:** Helvetica (standard, bold)

## Customization

To customize PDF appearance, edit `pdf_report_generator.py`:
- Modify color schemes in `colors.HexColor()` calls
- Adjust page size in `SimpleDocTemplate(pagesize=...)`
- Change fonts in `ParagraphStyle(fontName=...)`
- Add company logos using `Image()` flowable

## Performance

- PDF generation is fast (~1-2 seconds for typical reports)
- Memory efficient (uses temporary files)
- No impact on dashboard performance (generated on-demand)

## Security

- PDFs are generated in temporary directory
- No sensitive data is cached
- Files are cleaned up automatically after download
- Read-only access to source data
