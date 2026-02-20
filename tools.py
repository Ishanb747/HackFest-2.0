"""
tools.py — Custom CrewAI tools for Turgon.

Tools:
  1. DoclingPDFParserTool    — Parse regulatory PDFs with layout awareness
  2. RuleStoreWriterTool     — Save & deduplicate extracted rules to JSON
  3. SecureSQLValidatorTool  — Multi-layer read-only SQL enforcement
  4. DuckDBExecutionSandboxTool — Execute validated SQL against AML database
"""

from __future__ import annotations

import hashlib
import json
import re
import traceback
from pathlib import Path
from typing import Any, Type

import duckdb
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config import (
    DUCKDB_PATH,
    MAX_VIOLATION_ROWS,
    RULES_JSON_PATH,
)


# ══════════════════════════════════════════════════════════════════════════════
# 1. DOCLING PDF PARSER TOOL
# ══════════════════════════════════════════════════════════════════════════════


class DoclingPDFParserInput(BaseModel):
    pdf_path: str = Field(..., description="Absolute or relative path to the PDF file to parse.")


class DoclingPDFParserTool(BaseTool):
    """
    Parse a regulatory PDF using Docling, preserving tables and layout.
    Returns a single structured text string suitable for rule extraction.
    """

    name: str = "docling_pdf_parser"
    description: str = (
        "Parse a regulatory or compliance PDF file using the Docling library. "
        "Preserves tables, headings, and layout structure. "
        "Input: the absolute path to a PDF file. "
        "Output: full structured text content of the document."
    )
    args_schema: Type[BaseModel] = DoclingPDFParserInput

    def _run(self, pdf_path: str) -> str:
        try:
            from docling.document_converter import DocumentConverter
        except ImportError:
            return "ERROR: docling is not installed. Run: pip install docling"

        path = Path(pdf_path)
        if not path.exists():
            return f"ERROR: File not found at path '{pdf_path}'"
        if path.suffix.lower() != ".pdf":
            return f"ERROR: Expected a .pdf file, got '{path.suffix}'"

        # ── Attempt 1: Full pipeline (layout-aware, table detection) ─────────
        try:
            converter = DocumentConverter()
            result = converter.convert(str(path))
            markdown_text = result.document.export_to_markdown()
            pipeline_used = "standard"
        except Exception as e1:
            # ── Attempt 2: SimplePipeline (no ML layout model required) ──────
            # Triggered when transformers/model weights are missing or stale.
            try:
                from docling.pipeline.simple_pipeline import SimplePipeline
                from docling.datamodel.pipeline_options import PipelineOptions
                from docling.document_converter import DocumentConverter, PdfFormatOption
                from docling.datamodel.base_models import InputFormat

                opts = PipelineOptions(do_ocr=False, do_table_structure=False)
                converter2 = DocumentConverter(
                    format_options={
                        InputFormat.PDF: PdfFormatOption(pipeline_cls=SimplePipeline)
                    }
                )
                result2 = converter2.convert(str(path))
                markdown_text = result2.document.export_to_markdown()
                pipeline_used = f"simple (full pipeline failed: {str(e1)[:120]})"
            except Exception as e2:
                # ── Attempt 3: Raw pypdfium2 text extraction ──────────────────
                try:
                    import pypdfium2 as pdfium
                    pages = []
                    pdf_doc = pdfium.PdfDocument(str(path))
                    for i, page in enumerate(pdf_doc):
                        textpage = page.get_textpage()
                        pages.append(f"## Page {i+1}\n\n{textpage.get_text_range()}")
                    markdown_text = "\n\n".join(pages)
                    pipeline_used = f"raw-text (docling failed: {str(e2)[:80]})"
                except Exception as e3:
                    return (
                        f"ERROR: All PDF parsing strategies failed.\n"
                        f"  Standard pipeline: {str(e1)[:200]}\n"
                        f"  Simple pipeline:   {str(e2)[:200]}\n"
                        f"  pypdfium2 raw:     {str(e3)[:200]}\n\n"
                        f"{traceback.format_exc()}"
                    )

        header = (
            f"# Document: {path.name}\n"
            f"# Pipeline: {pipeline_used}\n\n"
        )
        full_text = header + markdown_text

        # Safety cap for very large documents
        if len(full_text) > 300_000:
            full_text = full_text[:300_000] + (
                "\n\n[TRUNCATED: Document exceeded 300,000 characters. "
                "Consider splitting the PDF into sections.]"
            )

        return full_text


# ══════════════════════════════════════════════════════════════════════════════
# 2. RULE STORE WRITER TOOL
# ══════════════════════════════════════════════════════════════════════════════


class RuleStoreWriterInput(BaseModel):
    rules_json: str = Field(
        ...,
        description=(
            "A JSON string containing a list of extracted policy rules. "
            "Each rule must have: id, rule_type, description, "
            "condition_field, operator, threshold_value, sql_hint."
        ),
    )


class PolicyRule(BaseModel):
    """Pydantic schema for a single extracted rule."""
    id: str
    rule_type: str
    description: str
    condition_field: str
    operator: str
    threshold_value: Any
    sql_hint: str


class RuleStoreWriterTool(BaseTool):
    """
    Validate, deduplicate (via SHA-256 fingerprint), and persist
    extracted policy rules to the local JSON rule store.
    """

    name: str = "rule_store_writer"
    description: str = (
        "Save extracted policy rules to the local JSON rule store. "
        "Accepts a JSON string of rule objects. Deduplicates rules automatically. "
        "Returns a summary of how many rules were saved or skipped."
    )
    args_schema: Type[BaseModel] = RuleStoreWriterInput

    def _fingerprint(self, rule: dict) -> str:
        """SHA-256 fingerprint based on condition_field + operator + threshold_value."""
        key = f"{rule.get('condition_field','')}.{rule.get('operator','')}.{rule.get('threshold_value','')}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def _run(self, rules_json: str) -> str:
        # ── Parse input ───────────────────────────────────────────────────────
        try:
            # Strip markdown code fences if the LLM wrapped the JSON
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", rules_json.strip(), flags=re.MULTILINE)
            incoming: list[dict] = json.loads(cleaned)
        except json.JSONDecodeError as e:
            return f"ERROR: Invalid JSON input — {e}"

        if not isinstance(incoming, list):
            incoming = [incoming]  # wrap single object

        # ── Validate with Pydantic ────────────────────────────────────────────
        valid_rules = []
        validation_errors = []
        for i, raw in enumerate(incoming):
            try:
                rule = PolicyRule(**raw)
                valid_rules.append(rule.model_dump())
            except Exception as e:
                validation_errors.append(f"Rule #{i}: {e}")

        if not valid_rules:
            return f"ERROR: No valid rules found.\nValidation errors:\n" + "\n".join(validation_errors)

        # ── Load existing rules ───────────────────────────────────────────────
        RULES_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        existing: list[dict] = []
        if RULES_JSON_PATH.exists():
            try:
                existing = json.loads(RULES_JSON_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = []

        existing_fps = {r.get("_fingerprint") for r in existing}

        # ── Deduplicate and merge ─────────────────────────────────────────────
        added = 0
        skipped = 0
        for rule in valid_rules:
            fp = self._fingerprint(rule)
            if fp in existing_fps:
                skipped += 1
            else:
                rule["_fingerprint"] = fp
                existing.append(rule)
                existing_fps.add(fp)
                added += 1

        # ── Persist ───────────────────────────────────────────────────────────
        RULES_JSON_PATH.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        summary = (
            f"Rule store updated: {added} new rule(s) added, "
            f"{skipped} duplicate(s) skipped. "
            f"Total rules in store: {len(existing)}. "
            f"Saved to: {RULES_JSON_PATH}"
        )
        if validation_errors:
            summary += f"\nValidation warnings: {'; '.join(validation_errors)}"
        return summary


# ══════════════════════════════════════════════════════════════════════════════
# 3. SECURE SQL VALIDATOR TOOL
# ══════════════════════════════════════════════════════════════════════════════


# Blocklist — any of these appearing in SQL (even in subqueries) are rejected
_DDL_DML_BLOCKLIST: tuple[str, ...] = (
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "CREATE",
    "ALTER",
    "TRUNCATE",
    "REPLACE",
    "MERGE",
    "EXEC",
    "EXECUTE",
    "CALL",
    "GRANT",
    "REVOKE",
    "COPY",
    "ATTACH",
    "DETACH",
    "LOAD",
    "IMPORT",
    "EXPORT",
)

# Allowlist — the only statement type permitted
_SELECT_PATTERN = re.compile(r"^\s*SELECT\b", re.IGNORECASE)

# Comment stripping patterns
_INLINE_COMMENT = re.compile(r"--[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


class SecureSQLValidatorInput(BaseModel):
    sql: str = Field(..., description="The SQL query string to validate.")


class SecureSQLValidatorTool(BaseTool):
    """
    Multi-layer security guardrail.

    Layer 1: Strip SQL comments (prevent disguising DDL inside comments)
    Layer 2: Enforce SELECT-only (allowlist approach)
    Layer 3: Token blocklist scan for DDL/DML keywords (even in subqueries)
    Layer 4: Semicolon injection check (prevent multi-statement attacks)

    Returns JSON: {"valid": true} or {"valid": false, "reason": "..."}
    """

    name: str = "secure_sql_validator"
    description: str = (
        "Validate that a SQL query is strictly read-only (SELECT only). "
        "Rejects any DDL or DML operations. "
        "Input: SQL query string. "
        "Output: JSON with 'valid' boolean and optional 'reason' for rejection."
    )
    args_schema: Type[BaseModel] = SecureSQLValidatorInput

    def _run(self, sql: str) -> str:
        if not sql or not sql.strip():
            return json.dumps({"valid": False, "reason": "Empty SQL string provided."})

        # ── Layer 1: Strip comments ───────────────────────────────────────────
        cleaned = _BLOCK_COMMENT.sub(" ", sql)
        cleaned = _INLINE_COMMENT.sub(" ", cleaned)
        cleaned = cleaned.strip()

        # ── Layer 2: Allowlist — must start with SELECT ───────────────────────
        if not _SELECT_PATTERN.match(cleaned):
            first_word = cleaned.split()[0].upper() if cleaned.split() else ""
            return json.dumps({
                "valid": False,
                "reason": (
                    f"Statement begins with '{first_word}', not SELECT. "
                    "Only read-only SELECT statements are permitted."
                ),
            })

        # ── Layer 3: Blocklist token scan ─────────────────────────────────────
        # Tokenise on word boundaries to avoid false positives
        # (e.g. "EXECUTE" inside a column alias like "execute_count" won't match)
        sql_upper = cleaned.upper()
        for blocked in _DDL_DML_BLOCKLIST:
            pattern = re.compile(r"\b" + re.escape(blocked) + r"\b")
            if pattern.search(sql_upper):
                return json.dumps({
                    "valid": False,
                    "reason": (
                        f"Blocked keyword '{blocked}' detected. "
                        "Turgon enforces strictly read-only queries."
                    ),
                })

        # ── Layer 4: Semicolon injection check ────────────────────────────────
        # Split on semicolon and count non-empty statements
        statements = [s.strip() for s in cleaned.split(";") if s.strip()]
        if len(statements) > 1:
            return json.dumps({
                "valid": False,
                "reason": (
                    f"Multiple statements detected ({len(statements)} statements separated by ';'). "
                    "Only a single SELECT statement is permitted per query."
                ),
            })

        return json.dumps({"valid": True})


# ══════════════════════════════════════════════════════════════════════════════
# 4. DUCKDB EXECUTION SANDBOX TOOL
# ══════════════════════════════════════════════════════════════════════════════


class DuckDBExecutionSandboxInput(BaseModel):
    sql: str = Field(..., description="The SELECT SQL query to execute against the AML database.")
    rule_id: str = Field(
        default="unknown",
        description="The rule ID associated with this query (for audit logging).",
    )


class DuckDBExecutionSandboxTool(BaseTool):
    """
    Execute a validated read-only SQL query against the AML DuckDB sandbox.

    Safety guarantees:
    - Runs SecureSQLValidatorTool FIRST — rejects any non-SELECT statement
    - Opens DuckDB in READ-ONLY mode — writes are physically impossible
    - Caps result rows at MAX_VIOLATION_ROWS to prevent memory DoS
    - All errors are caught and returned as JSON (never propagated)
    """

    name: str = "duckdb_execution_sandbox"
    description: str = (
        "Execute a validated read-only SELECT SQL query against the AML DuckDB sandbox. "
        "Always validates the SQL for safety before execution. "
        "Input: SQL query string and optional rule_id. "
        "Output: JSON with execution results or error details."
    )
    args_schema: Type[BaseModel] = DuckDBExecutionSandboxInput

    def _run(self, sql: str, rule_id: str = "unknown") -> str:
        # ── Step 1: Security validation FIRST ────────────────────────────────
        validator = SecureSQLValidatorTool()
        validation_result = json.loads(validator._run(sql))

        if not validation_result.get("valid"):
            return json.dumps({
                "rule_id": rule_id,
                "status": "BLOCKED",
                "reason": validation_result.get("reason"),
                "violations": [],
                "row_count": 0,
            })

        # ── Step 2: Check database exists ─────────────────────────────────────
        if not DUCKDB_PATH.exists():
            return json.dumps({
                "rule_id": rule_id,
                "status": "ERROR",
                "reason": (
                    f"DuckDB database not found at '{DUCKDB_PATH}'. "
                    "Run 'python data/setup_duckdb.py' first to load the AML dataset."
                ),
                "violations": [],
                "row_count": 0,
            })

        # ── Step 3: Execute in read-only sandbox ──────────────────────────────
        conn = None
        try:
            # read_only=True guarantees no writes at the DuckDB engine level
            conn = duckdb.connect(database=str(DUCKDB_PATH), read_only=True)

            # Add row cap via LIMIT if not already present
            sql_capped = sql.rstrip().rstrip(";")
            if not re.search(r"\bLIMIT\b", sql_capped, re.IGNORECASE):
                sql_capped = f"{sql_capped} LIMIT {MAX_VIOLATION_ROWS}"

            relation = conn.execute(sql_capped)
            columns = [desc[0] for desc in relation.description]
            rows = relation.fetchall()

            violations = [dict(zip(columns, row)) for row in rows]

            # Convert non-serializable types (dates, Decimal) to strings
            def _serialize(obj):
                try:
                    json.dumps(obj)
                    return obj
                except (TypeError, ValueError):
                    return str(obj)

            violations_serialized = [
                {k: _serialize(v) for k, v in row.items()}
                for row in violations
            ]

            return json.dumps({
                "rule_id": rule_id,
                "status": "SUCCESS",
                "sql_executed": sql_capped,
                "row_count": len(violations_serialized),
                "capped_at": MAX_VIOLATION_ROWS,
                "violations": violations_serialized,
            }, default=str)

        except duckdb.Error as e:
            return json.dumps({
                "rule_id": rule_id,
                "status": "SQL_ERROR",
                "reason": str(e),
                "violations": [],
                "row_count": 0,
            })
        except Exception as e:
            return json.dumps({
                "rule_id": rule_id,
                "status": "ERROR",
                "reason": f"Unexpected error: {str(e)}",
                "violations": [],
                "row_count": 0,
            })
        finally:
            if conn:
                conn.close()
