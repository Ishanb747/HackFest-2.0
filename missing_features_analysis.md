# Turgon - Missing Features from Flowchart

## Features Implemented but NOT Shown in Flowchart

### 1. **Adaptive Schema Detection & Column Mapping**
- **Location**: `data/setup_duckdb.py`
- **What it does**: Automatically detects CSV column names and maps them to canonical names
- **Why it matters**: Handles different CSV schema variations without hardcoding
- **Missing from flowchart**: No "Schema Normalization" or "Column Mapping" step shown

### 2. **Multi-Layer SQL Security Validation**
- **Location**: `tools.py` - `SecureSQLValidatorTool`
- **Layers**:
  - Layer 1: Comment stripping (prevent disguised DDL)
  - Layer 2: SELECT-only allowlist
  - Layer 3: DDL/DML keyword blocklist
  - Layer 4: Semicolon injection prevention
- **Missing from flowchart**: Only shows "Secure SQL Guardrail" - doesn't show the 4-layer defense

### 3. **Rule Deduplication via Fingerprinting**
- **Location**: `tools.py` - `RuleStoreWriterTool._fingerprint()`
- **What it does**: SHA-256 fingerprinting based on condition_field + operator + threshold
- **Why it matters**: Prevents duplicate rules when re-running Phase 1
- **Missing from flowchart**: No deduplication step shown in Phase 1

### 4. **Fallback PDF Parsing Pipeline**
- **Location**: `tools.py` - `DoclingPDFParserTool`
- **Fallback chain**:
  1. Full Docling pipeline (layout-aware, table detection)
  2. SimplePipeline (no ML models)
  3. Raw pypdfium2 text extraction
- **Missing from flowchart**: Only shows "Docling Parser" - no fallback strategy

### 5. **Deterministic Explanation Mode (No-LLM)**
- **Location**: `phase3_explainer.py` - `_deterministic_explanation()`
- **What it does**: Generates plain-English alerts without LLM calls
- **CLI flag**: `--no-llm`
- **Missing from flowchart**: Phase 3 only shows LLM path, no deterministic fallback

### 6. **Risk Level Classification**
- **Location**: `phase3_explainer.py` - `_risk_level()`
- **Thresholds**: HIGH (≥500), MEDIUM (≥50), LOW (≥1)
- **Missing from flowchart**: No risk scoring/classification step shown

### 7. **Batch Processing for SQL Generation**
- **Location**: `tasks.py` - `BATCH_HINT = 5`
- **What it does**: Processes rules in batches to avoid LLM context overflow
- **Missing from flowchart**: Phase 2 shows single-pass execution

### 8. **Immutable Audit Trail (SQLite)**
- **Location**: `audit.py`
- **Events logged**:
  - Pipeline runs (phase, duration, stats)
  - HITL decisions (analyst, action, notes)
  - Explanation generation runs
- **Append-only**: No UPDATE or DELETE operations
- **Missing from flowchart**: Shows "Immutable Audit Log" but doesn't show what events are logged

### 9. **HITL Decision State Management**
- **Location**: `hitl.py`
- **Actions**: CONFIRMED, DISMISSED, ESCALATED, PENDING
- **Persistence**: JSON file with timestamp + analyst tracking
- **Missing from flowchart**: Shows HITL dashboard but not the decision state machine

### 10. **Performance Indexes (Adaptive)**
- **Location**: `data/setup_duckdb.py` - `create_indexes_adaptive()`
- **Indexed columns**: amount_paid, amount_received, pay_format, is_laundering, from_bank, to_bank
- **Missing from flowchart**: No database optimization step shown

### 11. **Compliance Views (Adaptive)**
- **Location**: `data/setup_duckdb.py` - `create_views_adaptive()`
- **Views created**:
  - `account_summary` - aggregated account statistics
  - `high_value_transactions` - transactions ≥ $10,000
  - `currency_mismatch` - payment/receiving currency differs
  - `laundering_confirmed` - Is_Laundering = 1
- **Missing from flowchart**: No pre-computed views shown

### 12. **Row Capping & Memory Safety**
- **Location**: `config.py` - `MAX_VIOLATION_ROWS = 500`
- **What it does**: Prevents memory DoS from massive result sets
- **Missing from flowchart**: No safety limits shown in Phase 2

### 13. **JSON Extraction from LLM Output**
- **Location**: `main.py` - `_extract_json_array()`
- **Handles**:
  - Markdown code fences (```json)
  - Generic fences (```)
  - Raw JSON arrays
- **Missing from flowchart**: No LLM output parsing/cleaning step

### 14. **Windows UTF-8 Fix**
- **Location**: `main.py` (lines 24-29)
- **What it does**: Reconfigures stdout/stderr to UTF-8 for emoji support
- **Missing from flowchart**: No platform compatibility handling shown

### 15. **Phase Orchestration Modes**
- **Location**: `main.py` - `--phase` argument
- **Modes**: 1, 2, 3, 12, 23, 123 (combined phases)
- **Missing from flowchart**: Shows linear 1→2→3 flow only

### 16. **Streamlit Dashboard Features**
- **Location**: `app.py`
- **Features NOT in flowchart**:
  - KPI cards (total rules, violations, risk breakdown)
  - Last run timestamp
  - Violation cards with risk color coding
  - Sample violation display
  - Audit log viewer
  - HITL decision summary
  - PDF upload interface
  - Phase execution controls
- **Missing from flowchart**: Shows generic "Dashboard" - no UI details

### 17. **Schema Injection into Agent Context**
- **Location**: `tasks.py` - `AML_DB_SCHEMA` constant
- **What it does**: Injects exact column names into Phase 2 task description
- **Why it matters**: Agent doesn't need to query information_schema
- **Missing from flowchart**: No schema context injection shown

### 18. **Validation Error Reporting**
- **Location**: `tools.py` - `RuleStoreWriterTool`
- **What it does**: Pydantic validation with detailed error messages per rule
- **Missing from flowchart**: No validation feedback loop shown

### 19. **Read-Only Database Mode**
- **Location**: `tools.py` - `duckdb.connect(read_only=True)`
- **What it does**: Physical write protection at DuckDB engine level
- **Missing from flowchart**: Shows "Read-Only Replica" but not enforcement mechanism

### 20. **Continuous vs Manual Trigger Modes**
- **Location**: Flowchart shows "Trigger Mode" decision
- **Status**: NOT IMPLEMENTED in code
- **Current**: Only manual execution via CLI/Streamlit
- **Missing**: No scheduler, cron, or continuous monitoring

---

## Summary

**20 features implemented but missing from flowchart:**
- 15 features exist in code but not shown in diagram
- 5 features shown in diagram but with insufficient detail
- 1 feature shown in diagram but NOT implemented (continuous monitoring)

**Recommendation**: Update flowchart to show:
1. Multi-layer security validation
2. Adaptive schema detection
3. Rule deduplication
4. Fallback pipelines (PDF parsing, deterministic explanations)
5. Risk classification
6. Batch processing
7. Performance optimizations (indexes, views, row caps)
8. Detailed audit events
9. HITL state machine
10. Phase orchestration modes
