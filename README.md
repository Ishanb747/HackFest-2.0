# ⚖️ RuleForge — Autonomous Policy-to-Enforcement Engine

**RuleForge** transforms regulatory PDF documents into executable compliance checks using AI agents, secure SQL sandboxes, and human-in-the-loop governance. Built for financial institutions to automate AML/CFT policy enforcement while maintaining full audit trails and analyst oversight.

## 🎯 What It Does

RuleForge reads compliance PDFs (AML directives, FinCEN guidance, Basel III frameworks), extracts structured policy rules, translates them into SQL queries, executes them against transaction databases, and generates plain-English alerts for human analysts — all while maintaining immutable audit logs and multi-layer security.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 3. Load AML dataset
python data/setup_duckdb.py

# 4. Run the pipeline
python main.py --pdf uploads/aml_policy.pdf

# 5. Launch dashboard
streamlit run app.py
```

## 📋 Features

### 🤖 AI-Powered Agents (CrewAI + Groq)
- **RuleArchitectAgent**: Extracts structured rules from regulatory PDFs
- **QueryEngineerAgent**: Translates rules into validated SQL queries
- **ExplanationAgent**: Generates plain-English alerts for analysts

### 🔐 Multi-Layer Security
- **Layer 1**: Comment stripping (prevents disguised DDL)
- **Layer 2**: SELECT-only allowlist
- **Layer 3**: DDL/DML keyword blocklist
- **Layer 4**: Semicolon injection prevention
- **Read-only database mode**: Physical write protection at DuckDB engine level
- **Row capping**: 500-row limit prevents memory DoS

### 📦 Policy Versioning
- Automatic snapshots before rule updates
- Version manifest with timestamps and source tracking
- Compare current vs. archived rule sets
- Full rollback capability

### 👤 Human-in-the-Loop Dashboard
- Real-time KPI cards (rules triggered, violations, severity)
- Interactive violation cards with risk color-coding
- 4-state decision workflow: CONFIRMED, DISMISSED, ESCALATED, PENDING
- Sample violation viewer (first 5 rows per rule)
- SQL audit log with query validation status
- Compliance report export (JSON/CSV)

### 🔍 Adaptive Schema Detection
- Auto-maps CSV column names to canonical schema
- Handles different IBM AML dataset variations
- Creates performance indexes dynamically
- Generates compliance views (high-value transactions, currency mismatches)

### 📄 Fallback Pipelines
- **PDF parsing**: Full Docling → SimplePipeline → pypdfium2 raw text
- **SQL generation**: LLM agent → Deterministic builder
- **Explanations**: LLM-enriched → Template-based

### 📊 Immutable Audit Trail
- SQLite append-only log
- Tracks pipeline runs, HITL decisions, explanation generation
- Timestamped events with full context
- Compliance-ready reporting

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: RuleForge — PDF → Policy-as-Code                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │ Docling PDF  │ → │ Rule Extract │ → │ Fingerprint  │   │
│  │ Parser       │   │ Agent (LLM)  │   │ & Dedupe     │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
│                              ↓                              │
│                      policy_rules.json                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Phase 2: SecureMonitor — SQL Generation & Execution        │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │ Query        │ → │ 4-Layer SQL  │ → │ DuckDB       │   │
│  │ Engineer     │   │ Validator    │   │ Sandbox      │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
│                              ↓                              │
│                    violation_report.json                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Explainer — Plain-English Alerts                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │ Explanation  │ → │ Risk         │ → │ Action       │   │
│  │ Agent (LLM)  │   │ Classifier   │   │ Recommender  │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
│                              ↓                              │
│                     explanations.json                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Phase 4: HITL Dashboard — Human Governance                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │ Streamlit UI │ → │ Analyst      │ → │ Audit Log    │   │
│  │ (KPIs, Cards)│   │ Decisions    │   │ (SQLite)     │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
turgon/
├── main.py                  # CLI entrypoint (orchestrates phases)
├── app.py                   # Streamlit dashboard
├── config.py                # Central configuration
├── agents.py                # CrewAI agent definitions
├── tasks.py                 # CrewAI task definitions
├── tools.py                 # Custom tools (PDF parser, SQL validator, etc.)
├── phase2_executor.py       # Deterministic SQL generation (no LLM)
├── phase3_explainer.py      # LLM explanation generator
├── hitl.py                  # Human-in-the-loop decision storage
├── audit.py                 # Immutable audit trail (SQLite)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (GROQ_API_KEY)
│
├── data/
│   ├── setup_duckdb.py      # Load IBM AML dataset into DuckDB
│   ├── check_schema.py      # Verify database schema
│   ├── aml.db               # DuckDB database (read-only)
│   └── HI-Small_Trans.csv   # IBM AML dataset (download from Kaggle)
│
├── rules/
│   ├── policy_rules.json    # Extracted policy rules (current)
│   ├── violation_report.json # SQL execution results
│   ├── explanations.json    # Plain-English alerts
│   ├── policy_versions.json # Version manifest
│   ├── audit.db             # Audit trail (SQLite)
│   └── versions/            # Archived rule snapshots
│       └── policy_rules_v1__20260221T134349Z.json
│
└── uploads/
    └── test_aml_policy.pdf  # Sample regulatory PDF
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required: Groq API key for LLM access
GROQ_API_KEY=gsk_...

# Optional: Model selection (default: llama-3.1-8b-instant)
TURGON_MODEL=llama-3.3-70b-versatile
```

### Database Setup

Download the IBM AML dataset from [Kaggle](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml) and place CSV files in `data/`:

```bash
# Supported files (script tries each in order):
data/HI-Small_Trans.csv
data/HI-Medium_Trans.csv
data/HI-Large_Trans.csv
data/LI-Small_Trans.csv
data/LI-Medium_Trans.csv
data/LI-Large_Trans.csv
```

Then run:

```bash
python data/setup_duckdb.py
```

This creates:
- `data/aml.db` (DuckDB database)
- Adaptive indexes on key columns
- Compliance views (account_summary, high_value_transactions, etc.)

## 🎮 Usage

### CLI Commands

```bash
# Run all phases (default)
python main.py --pdf uploads/aml_policy.pdf

# Run specific phases
python main.py --pdf uploads/aml_policy.pdf --phase 1    # Extract rules only
python main.py --phase 2                                 # Execute existing rules
python main.py --phase 3                                 # Generate explanations
python main.py --phase 12                                # Extract + Execute
python main.py --phase 23                                # Execute + Explain

# Skip Phase 1 (use existing rules)
python main.py --skip-phase1 --phase 23

# Use deterministic explanation (no LLM)
python main.py --phase 3 --no-llm
```

### Dashboard

```bash
streamlit run app.py
```

Features:
- **Overview Tab**: KPI cards, violation charts, severity distribution
- **Policy Rules Tab**: Searchable rule table with filters, version comparison
- **Violations Tab**: Interactive cards with HITL decision buttons
- **AI Explanations Tab**: Plain-English alerts with risk classification
- **Audit Log Tab**: Immutable event history, SQL audit, compliance reports

## 🔒 Security Guarantees

### SQL Validation (4 Layers)

1. **Comment Stripping**: Removes `--` and `/* */` to prevent disguised DDL
2. **SELECT Allowlist**: Only queries starting with `SELECT` are permitted
3. **DDL/DML Blocklist**: Rejects `DROP`, `DELETE`, `UPDATE`, `INSERT`, `CREATE`, etc.
4. **Injection Prevention**: Blocks multi-statement attacks (semicolon separation)

### Database Protection

- **Read-only mode**: `duckdb.connect(read_only=True)` — writes physically impossible
- **Row capping**: 500-row limit on all queries
- **Sandboxed execution**: All queries validated before execution
- **Error isolation**: SQL errors never propagate to agents

### Audit Trail

- **Append-only**: SQLite log with no UPDATE/DELETE operations
- **Timestamped events**: Every pipeline run, HITL decision, explanation generation
- **Full context**: JSON details for every event
- **Compliance-ready**: Export reports for regulatory review

## 📊 Data Schema

### Policy Rule (policy_rules.json)

```json
{
  "id": "RULE_001",
  "rule_type": "threshold",
  "description": "Transactions exceeding $10,000 must be reported",
  "condition_field": "Amount_Paid",
  "operator": ">",
  "threshold_value": 10000,
  "sql_hint": "SELECT * FROM aml.transactions WHERE Amount_Paid > 10000",
  "_fingerprint": "a1b2c3d4e5f6g7h8"
}
```

### Violation Report (violation_report.json)

```json
{
  "rule_id": "RULE_001",
  "rule_description": "Transactions exceeding $10,000 must be reported",
  "sql": "SELECT From_Bank, Amount_Paid FROM aml.transactions WHERE Amount_Paid > 10000",
  "violation_count": 1234,
  "sample_violations": [
    {"From_Bank": "Bank A", "Amount_Paid": 15000.0},
    {"From_Bank": "Bank B", "Amount_Paid": 25000.0}
  ],
  "status": "SUCCESS"
}
```

### Explanation (explanations.json)

```json
{
  "rule_id": "RULE_001",
  "alert_headline": "1,234 Transactions Violate $10K Reporting Threshold",
  "plain_english": "Our automated compliance scan identified 1,234 transactions that exceed the $10,000 reporting threshold...",
  "risk_level": "HIGH",
  "violation_count": 1234,
  "recommended_action": "Immediately file a Suspicious Activity Report (SAR)...",
  "policy_reference": "Transactions exceeding $10,000 must be reported",
  "generated_by": "llm"
}
```

## 🧪 Testing

```bash
# Check database schema
python data/check_schema.py

# Generate test PDF
python generate_test_pdf.py

# Run Phase 2 standalone (deterministic)
python phase2_executor.py

# Run Phase 3 standalone
python phase3_explainer.py --no-llm
```

## 🛠️ Tech Stack

- **AI Framework**: CrewAI 0.80+ (multi-agent orchestration)
- **LLM**: Groq (Llama 3.3 70B Versatile)
- **Database**: DuckDB 1.1+ (embedded OLAP)
- **PDF Parsing**: Docling 2.3+ (layout-aware extraction)
- **Frontend**: Streamlit 1.41+ (interactive dashboard)
- **Visualization**: Plotly 5.20+ (charts and graphs)
- **Validation**: Pydantic 2.6+ (schema enforcement)
- **Audit**: SQLite (immutable log)

## 📈 Performance

- **Phase 1** (PDF → Rules): ~30-60s for 10-page PDF
- **Phase 2** (SQL Execution): ~5-10s for 20 rules
- **Phase 3** (Explanations): ~15-30s for 20 rules (LLM mode)
- **Dashboard**: Real-time updates with 5s cache TTL

## 🔄 Workflow Example

1. **Upload PDF**: Compliance officer uploads new AML directive
2. **Extract Rules**: RuleArchitectAgent parses PDF, extracts 15 rules
3. **Version Snapshot**: Previous 12 rules archived as v1
4. **Execute SQL**: QueryEngineerAgent generates + validates 15 queries
5. **Detect Violations**: 8 rules triggered, 2,345 total violations
6. **Generate Alerts**: ExplanationAgent creates plain-English summaries
7. **Analyst Review**: Compliance analyst reviews dashboard
8. **HITL Decisions**: 5 CONFIRMED, 2 DISMISSED, 1 ESCALATED
9. **Audit Log**: All events recorded with timestamps
10. **Export Report**: Compliance report generated for regulatory filing

## 🚧 Limitations

- **PDF Parsing**: Complex tables or scanned images may require manual review
- **SQL Generation**: Highly complex rules may need manual SQL refinement
- **LLM Accuracy**: Explanations should be reviewed by analysts
- **Dataset**: Currently supports IBM AML dataset schema only
- **Scalability**: Designed for 10-100 rules; larger rule sets may need batching

## 🗺️ Roadmap

- [ ] Multi-dataset support (SWIFT, FATF, FinCEN)
- [ ] Real-time monitoring (continuous execution mode)
- [ ] Advanced pattern detection (graph analytics)
- [ ] Multi-language support (Spanish, French, German)
- [ ] API endpoints (REST/GraphQL)
- [ ] Slack/Teams integration (alert notifications)
- [ ] Custom rule builder UI (no-code rule creation)

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/turgon/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/turgon/discussions)
- **Email**: support@turgon.dev

## 🙏 Acknowledgments

- **IBM**: AML dataset for testing
- **Groq**: Fast LLM inference
- **CrewAI**: Multi-agent framework
- **DuckDB**: Embedded analytics database
- **Docling**: PDF parsing library

---

**Built with ⚖️ by compliance engineers, for compliance engineers.**
