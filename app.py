"""
app.py — Turgon Human-in-the-Loop Dashboard (Streamlit)

Launch: streamlit run app.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Turgon — Policy Enforcement Engine",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).parent.resolve()
RULES_JSON   = ROOT / "rules" / "policy_rules.json"
VIOLATION_JSON = ROOT / "rules" / "violation_report.json"
UPLOADS_DIR  = ROOT / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# ── Light Theme CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

  /* ── Hide Streamlit chrome ──────────────────────── */
  header[data-testid="stHeader"] { background: #f8fafc !important; border-bottom: 1px solid #e2e8f0 !important; }
  [data-testid="stToolbar"] { display: none !important; }
  .stDeployButton { display: none !important; }
  #MainMenu { visibility: hidden !important; }
  footer { visibility: hidden !important; }

  /* ── Global ─────────────────────────────────────── */
  html, body, .stApp { background: #f0f4f8 !important; color: #1e293b; font-family: 'Inter', sans-serif; }
  h1,h2,h3,h4 { color: #0f172a !important; }

  /* ── Hero bar ───────────────────────────────────── */
  .hero-bar {
    background: linear-gradient(135deg, #1e40af 0%, #2563eb 50%, #1d4ed8 100%);
    border-bottom: 1px solid #1e40af;
    padding: 1.6rem 2rem 1.2rem;
    margin: -1rem -1rem 1.5rem -1rem;
    position: relative; overflow: hidden;
  }
  .hero-bar::before {
    content: ''; position: absolute; top: -60%; left: -30%;
    width: 160%; height: 220%;
    background: radial-gradient(ellipse at center, rgba(255,255,255,0.12) 0%, transparent 70%);
    animation: pulse-glow 6s ease-in-out infinite;
  }
  @keyframes pulse-glow { 0%,100% { opacity:.5; } 50% { opacity:1; } }
  .hero-title {
    font-size: 2rem; font-weight: 900; color: #fff;
    letter-spacing: -1px; margin: 0;
  }
  .hero-sub { color: rgba(255,255,255,.75); font-size: .9rem; margin-top: .2rem; font-weight: 400; }
  .hero-badges { margin-top: .8rem; display: flex; gap: .5rem; flex-wrap: wrap; }
  .hero-badge {
    display: inline-flex; align-items: center; gap: .35rem;
    background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3);
    color: #fff; border-radius: 20px; padding: 3px 12px;
    font-size: .72rem; font-weight: 600; letter-spacing: .3px;
  }

  /* ── KPI cards ──────────────────────────────────── */
  .kpi-grid { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
  .kpi-card {
    flex: 1; min-width: 160px;
    background: #ffffff;
    border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
    position: relative; overflow: hidden;
    transition: transform .15s, box-shadow .15s;
  }
  .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,.1); }
  .kpi-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px; border-radius: 14px 14px 0 0;
  }
  .kpi-card.blue::before  { background: linear-gradient(90deg,#1d4ed8,#3b82f6); }
  .kpi-card.red::before   { background: linear-gradient(90deg,#b91c1c,#ef4444); }
  .kpi-card.amber::before { background: linear-gradient(90deg,#b45309,#f59e0b); }
  .kpi-card.green::before { background: linear-gradient(90deg,#15803d,#22c55e); }
  .kpi-card.purple::before{ background: linear-gradient(90deg,#6d28d9,#a78bfa); }
  .kpi-label { font-size: .7rem; text-transform: uppercase; letter-spacing: 1.2px; color: #64748b; font-weight: 600; margin-bottom: .4rem; }
  .kpi-value { font-size: 2.2rem; font-weight: 800; line-height: 1; color: #0f172a; font-variant-numeric: tabular-nums; }
  .kpi-sub   { font-size: .74rem; color: #94a3b8; margin-top: .3rem; }
  .kpi-icon  { position: absolute; top: .9rem; right: 1rem; font-size: 1.5rem; opacity: .15; }

  /* ── Violation cards ────────────────────────────── */
  .v-card {
    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: .75rem;
    border-left: 4px solid; background: #fff;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
    transition: all .15s;
  }
  .v-card:hover { transform: translateX(2px); box-shadow: 0 4px 12px rgba(0,0,0,.1); }
  .v-card.high   { border-color: #ef4444; background: #fff5f5; }
  .v-card.medium { border-color: #f59e0b; background: #fffbeb; }
  .v-card.low    { border-color: #22c55e; background: #f0fdf4; }
  .v-card.clear  { border-color: #22c55e; background: #f0fdf4; }
  .v-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:.4rem; }
  .v-rule-id { font-weight: 700; font-size: 1rem; color: #0f172a; }
  .v-count { font-size: 1.6rem; font-weight: 800; }
  .v-count.high   { color: #dc2626; }
  .v-count.medium { color: #d97706; }
  .v-count.low    { color: #16a34a; }
  .v-desc  { color: #475569; font-size: .84rem; margin: .3rem 0 .5rem; line-height: 1.4; }
  .v-footer{ display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; }

  /* ── Badges ─────────────────────────────────────── */
  .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: .68rem; font-weight: 700; letter-spacing: .5px; text-transform: uppercase; }
  .badge-red    { background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; }
  .badge-amber  { background:#fef3c7; color:#d97706; border:1px solid #fcd34d; }
  .badge-green  { background:#dcfce7; color:#16a34a; border:1px solid #86efac; }
  .badge-blue   { background:#dbeafe; color:#1d4ed8; border:1px solid #93c5fd; }
  .badge-purple { background:#ede9fe; color:#6d28d9; border:1px solid #c4b5fd; }
  .badge-grey   { background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; }

  /* ── Section headings ───────────────────────────── */
  .sec-head {
    font-size: 1rem; font-weight: 700; color: #0f172a;
    border-bottom: 1px solid #e2e8f0; padding-bottom: .5rem; margin-bottom: 1rem;
    display: flex; align-items: center; gap: .5rem;
  }

  /* ── Sidebar ────────────────────────────────────── */
  section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
  section[data-testid="stSidebar"] .stMarkdown h2 { color: #1d4ed8 !important; }
  section[data-testid="stSidebar"] .stMarkdown p { color: #1e293b !important; }
  section[data-testid="stSidebar"] .stMarkdown h3 { color: #0f172a !important; }
  section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #1e293b !important; }
  section[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color: #64748b !important; }
  section[data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #0f172a !important; }
  section[data-testid="stSidebar"] .stRadio label p { color: #1e293b !important; }
  section[data-testid="stSidebar"] .stCaption p { color: #64748b !important; }
  section[data-testid="stSidebar"] [data-testid="stFileUploader"] { background: #f8fafc !important; border: 1px dashed #94a3b8 !important; border-radius: 8px !important; }
  section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] p { color: #1e293b !important; }
  section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span { color: #64748b !important; }

  /* ── Tabs ───────────────────────────────────────── */
  button[data-baseweb="tab"] { background: transparent !important; color: #64748b !important; font-weight: 600; transition: all .15s; }
  button[data-baseweb="tab"][aria-selected="true"] { color: #1d4ed8 !important; border-bottom: 2px solid #1d4ed8 !important; }

  /* ── Buttons ────────────────────────────────────── */
  .stButton > button { border-radius: 8px !important; font-weight: 600 !important; transition: all .15s !important; }
  [data-testid="baseButton-primary"] {
    background: linear-gradient(135deg,#1d4ed8,#2563eb) !important;
    border: none !important; color: #fff !important;
    box-shadow: 0 2px 8px rgba(29,78,216,.3) !important;
  }
  [data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(29,78,216,.4) !important;
  }

  /* ── Code / pre ─────────────────────────────────── */
  pre, code { background: #f8fafc !important; border: 1px solid #e2e8f0 !important; border-radius: 8px !important; font-size: .82rem !important; color: #1e293b !important; }

  /* ── Log box ────────────────────────────────────── */
  .log-box {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: .8rem 1rem; font-family: monospace; font-size: .78rem;
    color: #166534; max-height: 360px; overflow-y: auto; line-height: 1.5;
  }

  /* ── Streamlit overrides ────────────────────────── */
  .stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
  div[data-testid="stMetric"] { background: #fff; border-radius: 10px; padding: .8rem; border: 1px solid #e2e8f0 !important; }
  div[data-testid="stMetric"] label { color: #64748b !important; }
  hr { border-color: #e2e8f0 !important; margin: 1.5rem 0 !important; }
  details summary { color: #1d4ed8 !important; font-weight: 600; font-size: .85rem; }
  details { border: 1px solid #e2e8f0 !important; border-radius: 8px !important; }
  [data-testid="stFileUploader"] { background: #fff !important; border: 1px solid #e2e8f0 !important; border-radius: 8px !important; }
  .stSelectbox [data-baseweb="select"] > div { background: #fff !important; border-color: #cbd5e1 !important; }
  .stTextInput > div > div { background: #fff !important; border-color: #cbd5e1 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _extract_json_list(text: str) -> list | None:
    m = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
    if m:
        try: return json.loads(m.group(1))
        except Exception: pass
    m = re.search(r"```\s*(\[.*?\])\s*```", text, re.DOTALL)
    if m:
        try: return json.loads(m.group(1))
        except Exception: pass
    start = text.find("["); end = text.rfind("]") + 1
    if start >= 0 and end > start:
        try: return json.loads(text[start:end])
        except Exception: pass
    return None


@st.cache_data(ttl=5)
def load_rules() -> list[dict]:
    if RULES_JSON.exists():
        try: return json.loads(RULES_JSON.read_text(encoding="utf-8"))
        except Exception: pass
    return []


@st.cache_data(ttl=5)
def load_violations() -> list[dict]:
    if VIOLATION_JSON.exists():
        try:
            raw = VIOLATION_JSON.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, list): return data
            if isinstance(data, dict) and "violations" in data: return data["violations"]
        except json.JSONDecodeError:
            raw = VIOLATION_JSON.read_text(encoding="utf-8")
            extracted = _extract_json_list(raw)
            if extracted: return extracted
        except Exception: pass
    return []


@st.cache_data(ttl=5)
def load_explanations() -> list[dict]:
    p = ROOT / "rules" / "explanations.json"
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except Exception: pass
    return []


def load_hitl_decisions() -> dict[str, dict]:
    """Load HITL decisions (not cached — must always be fresh)."""
    try:
        from hitl import load_decisions
        return load_decisions()
    except Exception:
        return {}


@st.cache_data(ttl=10)
def load_audit_log() -> list[dict]:
    try:
        from audit import get_log
        return get_log(limit=200)
    except Exception:
        return []


@st.cache_data(ttl=5)
def load_version_manifest() -> list[dict]:
    """Load policy version history (newest first)."""
    try:
        from tools import load_version_manifest as _lvm
        return _lvm()
    except Exception:
        return []


def load_rules_at_version(version: int) -> list[dict]:
    """Load archived rules for a specific version number."""
    try:
        from tools import load_rules_at_version as _lrav
        return _lrav(version)
    except Exception:
        return []


def severity_cls(count: int) -> str:
    if count == 0: return "clear"
    if count < 50: return "low"
    if count < 500: return "medium"
    return "high"


def badge(text: str, style: str) -> str:
    return f'<span class="badge badge-{style}">{text}</span>'


def last_run_str() -> str:
    if VIOLATION_JSON.exists():
        t = VIOLATION_JSON.stat().st_mtime
        return datetime.fromtimestamp(t).strftime("%d %b %Y · %H:%M:%S")
    return "Never"


# ═══════════════════════════════════════════════════════════════════════════
# Hero bar
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero-bar">
  <div class="hero-title">⚖️ Turgon</div>
  <div class="hero-sub">Autonomous Policy-to-Enforcement Engine</div>
  <div class="hero-badges">
    <span class="hero-badge">🤖 CrewAI</span>
    <span class="hero-badge">🦆 DuckDB</span>
    <span class="hero-badge">📄 Docling PDF</span>
    <span class="hero-badge">🔐 Read-only SQL Sandbox</span>
    <span class="hero-badge">🧠 OpenRouter LLM</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚖️ Turgon")
    st.caption("Autonomous Policy-to-Enforcement Engine")
    st.divider()

    st.markdown("### 📄 Upload Policy PDF")
    uploaded_file = st.file_uploader(
        "Drop a regulatory PDF here",
        type=["pdf"],
        help="Upload an AML/compliance PDF to extract rules and detect violations",
        label_visibility="collapsed",
    )

    st.markdown("### ⚙️ Run phases")
    run_phase = st.radio(
        "Run phases",
        options=[
            "All Phases (1 + 2 + 3)",
            "Phase 1 + 2 (Extract + SQL)",
            "Phase 1 only — Extract Rules",
            "Phase 2 only — Execute SQL",
            "Phase 3 only — Explain Violations",
        ],
        index=0,
        label_visibility="collapsed",
    )

    c1, c2 = st.columns(2)
    with c1:
        run_btn = st.button("🚀 Run", width='stretch', type="primary")
    with c2:
        if st.button("🔄 Refresh", width='stretch'):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    # Live stats
    rules      = load_rules()
    violations = load_violations()

    total_v    = sum(v.get("violation_count", 0) for v in violations)
    triggered  = sum(1 for v in violations if v.get("violation_count", 0) > 0)
    high_sev   = sum(1 for v in violations if v.get("violation_count", 0) >= 500)

    st.markdown("### 📊 Current State")
    st.metric("Rules in store",        len(rules))
    st.metric("Rules triggered",       f"{triggered} / {len(violations)}" if violations else "—")
    st.metric("Total violations",      f"{total_v:,}" if violations else "—")
    st.metric("High-severity rules",   high_sev)
    st.caption(f"Last run: {last_run_str()}")

    st.divider()

    # ── Policy Version History ────────────────────────────────────────────────
    st.markdown("### 📦 Policy Versions")
    version_manifest = load_version_manifest()

    if not version_manifest:
        st.caption("No versions yet. Run Phase 1 to create the first snapshot.")
    else:
        # Build label options
        version_labels = {
            f"v{e['version']} — {e['timestamp'][:10]} ({e['rule_count']} rules) [{e['pdf_source']}]": e["version"]
            for e in version_manifest
        }
        selected_label = st.selectbox(
            "Compare version",
            options=["▶ Current (live)"] + list(version_labels.keys()),
            label_visibility="collapsed",
        )

        if selected_label != "▶ Current (live)":
            selected_ver = version_labels[selected_label]
            archived_rules = load_rules_at_version(selected_ver)

            st.caption(f"Showing **v{selected_ver}** — {len(archived_rules)} rules")

            if archived_rules and rules:
                current_fps  = {r.get("_fingerprint") for r in rules}
                archived_fps = {r.get("_fingerprint") for r in archived_rules}
                added_count   = len(current_fps - archived_fps)
                removed_count = len(archived_fps - current_fps)
                col_a, col_b = st.columns(2)
                col_a.metric("Added since", f"+{added_count}", delta=added_count if added_count else None)
                col_b.metric("Removed since", f"-{removed_count}", delta=-removed_count if removed_count else None, delta_color="inverse")

            if st.button("📋 Show archived rules", use_container_width=True):
                st.session_state["show_archived_version"] = selected_ver
        else:
            # Clear any previously pinned version view
            st.session_state.pop("show_archived_version", None)


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline Runner
# ═══════════════════════════════════════════════════════════════════════════

if run_btn:
    if uploaded_file is None and "Phase 1" in run_phase:
        st.error("⚠️ Please upload a PDF before running Phase 1.")
    else:
        pdf_path = None
        if uploaded_file:
            pdf_path = UPLOADS_DIR / uploaded_file.name
            pdf_path.write_bytes(uploaded_file.read())

        phase_flag = (
            "123" if "All Phases" in run_phase else
            "12"  if "Phase 1 + 2" in run_phase else
            "1"   if "Phase 1 only" in run_phase else
            "2"   if "Phase 2 only" in run_phase else
            "3"
        )

        venv_python = ROOT / "venv" / "Scripts" / "python.exe"
        python_exe  = str(venv_python) if venv_python.exists() else sys.executable
        cmd = [python_exe, str(ROOT / "main.py"), "--phase", phase_flag]
        if pdf_path:
            cmd += ["--pdf", str(pdf_path)]
        elif phase_flag in ("1", "12", "123"):
            st.error("No PDF available. Upload a PDF or choose Phase 2/3 only.")
            st.stop()

        prog_area = st.empty()
        log_area  = st.empty()

        with prog_area.container():
            st.info(f"⏳ Running Phase {'1 + 2' if phase_flag == '12' else phase_flag}… this may take a few minutes.")

        log_lines: list[str] = []
        with st.spinner(""):
            try:
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, cwd=str(ROOT), encoding="utf-8", errors="replace",
                )
                for line in process.stdout:  # type: ignore
                    log_lines.append(line.rstrip())
                    log_area.markdown(
                        '<div class="log-box">' +
                        "\n".join(log_lines[-80:]).replace("<", "&lt;").replace(">", "&gt;") +
                        "</div>",
                        unsafe_allow_html=True,
                    )
                process.wait()

                if process.returncode == 0:
                    prog_area.success("✅ Pipeline completed! Reloading dashboard…")
                    st.cache_data.clear()
                    time.sleep(1.5)
                    st.rerun()
                else:
                    prog_area.error("❌ Pipeline exited with errors. Check log above.")
            except Exception as e:
                st.exception(e)


# ═══════════════════════════════════════════════════════════════════════════
# Main tabs
# ═══════════════════════════════════════════════════════════════════════════

rules        = load_rules()
violations   = load_violations()
explanations = load_explanations()

tab_overview, tab_rules, tab_violations, tab_explain, tab_hitl_log = st.tabs([
    "📈 Overview", "📋 Policy Rules", "🚨 Violations", "🤖 AI Explanations", "📋 Audit Log"
])


# ── TAB 1: Overview ─────────────────────────────────────────────────────────
with tab_overview:
    total_rules  = len(rules)
    total_v      = sum(v.get("violation_count", 0) for v in violations)
    triggered    = sum(1 for v in violations if v.get("violation_count", 0) > 0)
    high_sev     = sum(1 for v in violations if v.get("violation_count", 0) >= 500)
    blocked      = sum(1 for v in violations if v.get("status") == "BLOCKED")

    # KPI row
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-icon">📋</div>
        <div class="kpi-label">Policy Rules</div>
        <div class="kpi-value">{total_rules}</div>
        <div class="kpi-sub">extracted from PDF</div>
      </div>
      <div class="kpi-card amber">
        <div class="kpi-icon">⚡</div>
        <div class="kpi-label">Rules Triggered</div>
        <div class="kpi-value">{triggered}</div>
        <div class="kpi-sub">of {len(violations)} checked</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-icon">🚨</div>
        <div class="kpi-label">Total Violations</div>
        <div class="kpi-value">{total_v:,}</div>
        <div class="kpi-sub">across all rules</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-icon">🔥</div>
        <div class="kpi-label">High Severity</div>
        <div class="kpi-value">{high_sev}</div>
        <div class="kpi-sub">≥ 500 violations</div>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-icon">🛡️</div>
        <div class="kpi-label">Queries Blocked</div>
        <div class="kpi-value">{blocked}</div>
        <div class="kpi-sub">by SQL guardrail</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if violations:
        import plotly.graph_objects as go
        import plotly.express as px

        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown('<div class="sec-head">📊 Violations by Rule</div>', unsafe_allow_html=True)
            vdf = pd.DataFrame([
                {
                    "Rule": v.get("rule_id", "?"),
                    "Violations": v.get("violation_count", 0),
                    "Status": v.get("status", "?"),
                }
                for v in violations
            ]).sort_values("Violations", ascending=True)

            colors = []
            for cnt in vdf["Violations"]:
                if cnt >= 500: colors.append("#f85149")
                elif cnt >= 50: colors.append("#e3b341")
                else: colors.append("#3fb950")

            fig = go.Figure(go.Bar(
                x=vdf["Violations"], y=vdf["Rule"],
                orientation="h",
                marker=dict(color=colors, line=dict(width=0)),
                hovertemplate="<b>%{y}</b><br>Violations: %{x:,}<extra></extra>",
            ))
            fig.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=20, l=0, r=20),
                height=360,
                xaxis=dict(title="Violation Count", gridcolor="#e2e8f0", color="#475569"),
                yaxis=dict(title=None, tickfont=dict(size=11, color="#1e293b")),
                font=dict(family="Inter", color="#1e293b"),
            )
            st.plotly_chart(fig, width='stretch')

        with col_right:
            st.markdown('<div class="sec-head">🔵 Severity Distribution</div>', unsafe_allow_html=True)
            sev_counts = {"High (≥500)": 0, "Medium (50-499)": 0, "Low (<50)": 0, "Clear": 0}
            for v in violations:
                c = v.get("violation_count", 0)
                if c >= 500: sev_counts["High (≥500)"] += 1
                elif c >= 50: sev_counts["Medium (50-499)"] += 1
                elif c > 0:  sev_counts["Low (<50)"] += 1
                else:        sev_counts["Clear"] += 1

            fig2 = go.Figure(go.Pie(
                labels=list(sev_counts.keys()),
                values=list(sev_counts.values()),
                hole=0.55,
                marker=dict(colors=["#f85149", "#e3b341", "#3fb950", "#1e2d40"]),
                textfont=dict(color="#e6edf3"),
            ))
            fig2.update_traces(
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Rules: %{value}<extra></extra>",
            )
            fig2.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=0, b=0, l=0, r=0),
                height=300,
                showlegend=False,
                font=dict(family="Inter", color="#1e293b"),
                annotations=[dict(
                    text=f"<b>{len(violations)}</b><br>rules",
                    x=.5, y=.5, font_size=16, showarrow=False, font_color="#0f172a",
                )],
            )
            st.plotly_chart(fig2, width='stretch')

            # Rule type donut
            if rules:
                st.markdown('<div class="sec-head" style="margin-top:.5rem;">📦 Rule Types</div>', unsafe_allow_html=True)
                type_counts = pd.Series([r.get("rule_type", "unknown") for r in rules]).value_counts()
                fig3 = go.Figure(go.Pie(
                    labels=type_counts.index.tolist(),
                    values=type_counts.values.tolist(),
                    hole=0.5,
                    marker=dict(colors=["#58a6ff","#f85149","#e3b341","#3fb950","#bc8cff","#79c0ff"]),
                ))
                fig3.update_traces(textinfo="percent", hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>")
                fig3.update_layout(
                    template="plotly_white",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=220,
                    font=dict(family="Inter", color="#1e293b"),
                    legend=dict(orientation="v", font=dict(size=11, color="#1e293b"), x=1.05),
                )
                st.plotly_chart(fig3, width='stretch')

    else:
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem; color:#6e7f8d;">
          <div style="font-size:3rem; margin-bottom:.5rem;">📄</div>
          <div style="font-size:1.1rem; font-weight:600; color:#8b949e; margin-bottom:.3rem;">No data yet</div>
          <div style="font-size:.85rem;">Upload a regulatory PDF in the sidebar and click <strong style="color:#58a6ff;">Run</strong> to begin</div>
        </div>
        """, unsafe_allow_html=True)


# ── TAB 2: Policy Rules ──────────────────────────────────────────────────────
with tab_rules:
    # ── Archived version viewer (shown when user selects a version in sidebar) ─
    pinned_ver = st.session_state.get("show_archived_version")
    if pinned_ver is not None:
        archived_rules = load_rules_at_version(pinned_ver)
        st.info(f"📦 Viewing archived **v{pinned_ver}** — {len(archived_rules)} rules  ·  "
                f"[Click **▶ Current (live)** in sidebar to return to live view]")
        if archived_rules:
            arch_df = pd.DataFrame([
                {
                    "ID":          r.get("id"),
                    "Type":        r.get("rule_type", "—"),
                    "Field":       r.get("condition_field", "—"),
                    "Op":          r.get("operator", "—"),
                    "Threshold":   r.get("threshold_value", "—"),
                    "Description": r.get("description", ""),
                }
                for r in archived_rules
            ])
            st.dataframe(arch_df, use_container_width=True, hide_index=True,
                         column_config={"Description": st.column_config.TextColumn(width="large")})
            st.download_button(
                f"⬇️ Export v{pinned_ver} JSON",
                data=json.dumps(archived_rules, indent=2),
                file_name=f"turgon_rules_v{pinned_ver}.json",
                mime="application/json",
            )
        st.divider()

    if not rules:
        st.info("No policy rules extracted yet. Upload a regulatory PDF and run Phase 1.")
    else:
        col_s, col_t, col_op = st.columns([3, 1.5, 1.5])
        with col_s:
            search = st.text_input("🔍 Search rules", placeholder="threshold, bank, currency…", label_visibility="collapsed")
        with col_t:
            type_opts = ["All types"] + sorted(set(r.get("rule_type", "unknown") for r in rules))
            sel_type  = st.selectbox("Type", type_opts, label_visibility="collapsed")
        with col_op:
            sel_op = st.selectbox("Operator", ["All"] + sorted(set(r.get("operator", "?") for r in rules)), label_visibility="collapsed")

        filtered = rules
        if search:
            s = search.lower()
            filtered = [r for r in filtered if s in r.get("description","").lower()
                        or s in r.get("condition_field","").lower()
                        or s in r.get("sql_hint","").lower()]
        if sel_type != "All types":
            filtered = [r for r in filtered if r.get("rule_type") == sel_type]
        if sel_op != "All":
            filtered = [r for r in filtered if r.get("operator") == sel_op]

        # join violation counts
        v_map = {v.get("rule_id"): v.get("violation_count", 0) for v in violations}

        st.caption(f"Showing **{len(filtered)}** of **{len(rules)}** rules")

        df = pd.DataFrame([
            {
                "ID": r.get("id"),
                "Type": r.get("rule_type","—"),
                "Field": r.get("condition_field","—"),
                "Op": r.get("operator","—"),
                "Threshold": r.get("threshold_value","—"),
                "Violations": v_map.get(r.get("id",""), "—"),
                "Description": r.get("description",""),
                "SQL Hint": r.get("sql_hint",""),
            }
            for r in filtered
        ])
        st.dataframe(
            df, width='stretch', hide_index=True,
            column_config={
                "Description": st.column_config.TextColumn(width="large"),
                "SQL Hint": st.column_config.TextColumn(width="medium"),
                "Violations": st.column_config.NumberColumn(format="%d"),
            },
        )

        c1, c2 = st.columns([1, 5])
        with c1:
            st.download_button(
                "⬇️ Export JSON", data=json.dumps(filtered, indent=2),
                file_name="turgon_rules.json", mime="application/json",
            )


# ── TAB 3: Violations ────────────────────────────────────────────────────────
with tab_violations:
    if not violations:
        st.info("No violation report found. Run the full pipeline (Phase 1 + 2) first.")
    else:
        col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
        with col_f1:
            show_only = st.checkbox("Show only triggered rules", value=True)
        with col_f2:
            sev_filter = st.multiselect(
                "Severity", ["HIGH", "MEDIUM", "LOW", "CLEAR"],
                default=["HIGH", "MEDIUM", "LOW"],
                label_visibility="collapsed",
            )
        with col_f3:
            sort_by = st.selectbox("Sort", ["Violations ↓", "Violations ↑", "Rule ID"], label_visibility="collapsed")

        # Sort
        if sort_by == "Violations ↓":
            display_v = sorted(violations, key=lambda x: x.get("violation_count", 0), reverse=True)
        elif sort_by == "Violations ↑":
            display_v = sorted(violations, key=lambda x: x.get("violation_count", 0))
        else:
            display_v = sorted(violations, key=lambda x: x.get("rule_id", ""))

        st.divider()
        all_rows = []

        for idx, v in enumerate(display_v):
            rule_id     = v.get("rule_id", "?")
            description = v.get("rule_description", "No description")
            count       = v.get("violation_count", 0)
            status      = v.get("status", "?")
            sql         = v.get("sql", "")
            samples     = v.get("sample_violations", [])

            sev = severity_cls(count)
            sev_label = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW", "clear": "CLEAR"}[sev]

            if show_only and count == 0: continue
            if sev_label not in sev_filter: continue

            badge_sev_color = {"HIGH": "red", "MEDIUM": "amber", "LOW": "green", "CLEAR": "green"}.get(sev_label, "blue")
            status_color    = {"SUCCESS": "green", "BLOCKED": "red", "SQL_ERROR": "amber", "SKIPPED": "grey"}.get(status, "blue")

            # HITL decision badge
            hitl_decisions = load_hitl_decisions()
            current_decision = hitl_decisions.get(rule_id, {}).get("action", "PENDING")
            hitl_color = {"CONFIRMED": "green", "DISMISSED": "grey", "ESCALATED": "red", "PENDING": "blue"}.get(current_decision, "blue")

            st.markdown(f"""
            <div class="v-card {sev}">
              <div class="v-header">
                <span class="v-rule-id">{rule_id}</span>
                <div style="display:flex;gap:.4rem;align-items:center;">
                  {badge(sev_label, badge_sev_color)}
                  {badge(status, status_color)}
                  {badge('👤 ' + current_decision, hitl_color)}
                </div>
              </div>
              <div class="v-desc">{description}</div>
              <div class="v-footer">
                <span class="v-count {sev}">{count:,}</span>
                <span style="color:#6e7f8d;font-size:.82rem;margin-left:.3rem;">violations detected</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # HITL action buttons
            b1, b2, b3, b4 = st.columns([1, 1, 1, 3])
            with b1:
                if st.button("✅ Confirm", key=f"confirm_{rule_id}_{idx}"):
                    from hitl import save_decision
                    from audit import log_hitl_decision
                    save_decision(rule_id, "CONFIRMED")
                    log_hitl_decision(rule_id, "CONFIRMED", "analyst", "")
                    st.cache_data.clear()
                    st.rerun()
            with b2:
                if st.button("❌ Dismiss", key=f"dismiss_{rule_id}_{idx}"):
                    from hitl import save_decision
                    from audit import log_hitl_decision
                    save_decision(rule_id, "DISMISSED")
                    log_hitl_decision(rule_id, "DISMISSED", "analyst", "")
                    st.cache_data.clear()
                    st.rerun()
            with b3:
                if st.button("🚨 Escalate", key=f"escalate_{rule_id}_{idx}"):
                    from hitl import save_decision
                    from audit import log_hitl_decision
                    save_decision(rule_id, "ESCALATED")
                    log_hitl_decision(rule_id, "ESCALATED", "analyst", "Escalated for senior review")
                    st.cache_data.clear()
                    st.rerun()

            if samples:
                with st.expander(f"🔍 View sample violations ({min(len(samples),5)} shown)"):
                    st.dataframe(pd.DataFrame(samples[:5]), width='stretch', hide_index=True)

            if sql:
                with st.expander("🔧 View SQL used"):
                    st.code(sql, language="sql")

            st.divider()
            for row in samples:
                all_rows.append({"rule_id": rule_id, "severity": sev_label, **row})

        if all_rows:
            export_df = pd.DataFrame(all_rows)
            st.download_button(
                "⬇️ Export All Violations (CSV)",
                data=export_df.to_csv(index=False),
                file_name=f"turgon_violations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                width='stretch',
            )


# ── TAB 4: AI Explanations ────────────────────────────────────────────────────
with tab_explain:
    if not explanations:
        st.info(
            "No AI explanations yet. Run **All Phases (1 + 2 + 3)** or **Phase 3 only** from the sidebar.\n\n"
            "Phase 3 uses the LLM to generate plain-English alerts from the violation data."
        )
    else:
        exp_map = {e.get("rule_id"): e for e in explanations}
        triggered_exps = [e for e in explanations if e.get("risk_level") not in ("CLEAR", "", None)]
        clear_exps     = [e for e in explanations if e.get("risk_level") == "CLEAR"]

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Active Alerts", len(triggered_exps))
        col_b.metric("Clear (Compliant)", len(clear_exps))
        col_c.metric("AI Generated", sum(1 for e in explanations if e.get("generated_by") == "llm"))

        st.divider()
        risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "CLEAR": 3}
        sorted_exps = sorted(explanations, key=lambda e: risk_order.get(e.get("risk_level", "LOW"), 2))

        for exp in sorted_exps:
            risk  = exp.get("risk_level", "LOW")
            rid   = exp.get("rule_id", "?")
            count = exp.get("violation_count", 0)
            gen   = exp.get("generated_by", "deterministic")

            sev_card = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low", "CLEAR": "clear"}.get(risk, "low")
            risk_badge_color = {"HIGH": "red", "MEDIUM": "amber", "LOW": "green", "CLEAR": "green"}.get(risk, "blue")
            gen_badge = badge("🤖 AI" if gen == "llm" else "⚙️ Deterministic", "blue" if gen == "llm" else "grey")

            st.markdown(f"""
            <div class="v-card {sev_card}">
              <div class="v-header">
                <span class="v-rule-id">{rid} — {exp.get('alert_headline', '')}</span>
                <div style="display:flex;gap:.4rem;">
                  {badge(risk, risk_badge_color)}
                  {gen_badge}
                </div>
              </div>
              <div class="v-desc">{exp.get('plain_english', '')}</div>
              <div class="v-footer">
                <span class="v-count {sev_card}" style="font-size:1.1rem;">{count:,}</span>
                <span style="color:#475569;font-size:.82rem;margin-left:.4rem;">violations</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📋 Recommended Action & Policy Reference"):
                st.markdown(f"**Recommended Action:** {exp.get('recommended_action', '—')}")
                st.markdown(f"**Policy Reference:** *{exp.get('policy_reference', '—')}*")

        st.divider()
        st.download_button(
            "⬇️ Export Explanations (JSON)",
            data=json.dumps(explanations, indent=2),
            file_name=f"turgon_explanations_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
        )


# ── TAB 5: Audit Log ─────────────────────────────────────────────────────────
with tab_hitl_log:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="sec-head">📋 Immutable Audit Log</div>', unsafe_allow_html=True)
        st.caption("Every pipeline run and human decision is recorded here. Append-only — no modifications permitted.")

        audit_rows = load_audit_log()
        if not audit_rows:
            st.info("No audit events yet. Run the pipeline to begin recording.")
        else:
            audit_stats_col1, audit_stats_col2, audit_stats_col3 = st.columns(3)
            try:
                from audit import get_stats
                stats = get_stats()
                audit_stats_col1.metric("Total Events", stats.get("total_events", 0))
                audit_stats_col2.metric("Pipeline Runs", stats.get("pipeline_runs", 0))
                audit_stats_col3.metric("HITL Decisions", stats.get("hitl_decisions", 0))
            except Exception:
                pass

            st.divider()
            event_icons = {
                "PIPELINE_RUN": "🔄",
                "HITL_CONFIRMED": "✅",
                "HITL_DISMISSED": "❌",
                "HITL_ESCALATED": "🚨",
                "EXPLANATION_RUN": "🤖",
            }
            for row in audit_rows:
                icon = event_icons.get(row.get("event_type", ""), "📌")
                ts   = row.get("ts", "")[:19].replace("T", " ")
                evtype = row.get("event_type", "")
                rid  = row.get("rule_id") or "—"
                phase = row.get("phase", "")
                try:
                    details = json.loads(row.get("details_json") or "{}")
                except Exception:
                    details = {}

                with st.expander(f"{icon} [{ts} UTC] {phase} · {evtype} · rule: {rid}"):
                    st.json(details)

    with col_right:
        st.markdown('<div class="sec-head">🔐 SQL Audit</div>', unsafe_allow_html=True)
        st.caption("All queries validated by the Secure Monitor (SELECT-only sandbox).")

        if violations:
            status_icons = {"SUCCESS": "✅", "BLOCKED": "🚫", "SQL_ERROR": "❌", "SKIPPED": "⏭️"}
            for v in violations:
                rid    = v.get("rule_id", "?")
                sql    = v.get("sql", "No SQL recorded")
                status = v.get("status", "?")
                count  = v.get("violation_count", 0)
                icon   = status_icons.get(status, "⚠️")
                with st.expander(f"{icon} {rid} — {count:,} hits — {status}"):
                    st.code(sql, language="sql")
                    if v.get("reason"):
                        st.warning(f"Reason: {v['reason']}")
        else:
            st.info("No SQL audit log yet.")

        st.divider()
        st.markdown('<div class="sec-head">📄 Compliance Report</div>', unsafe_allow_html=True)

        # Generate compliance report on demand
        hitl_decisions = load_hitl_decisions()
        if violations:
            report_data = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "pipeline_summary": {
                    "rules_checked": len(violations),
                    "rules_triggered": sum(1 for v in violations if v.get("violation_count", 0) > 0),
                    "total_violations": sum(v.get("violation_count", 0) for v in violations),
                },
                "hitl_summary": {
                    "confirmed": sum(1 for d in hitl_decisions.values() if d.get("action") == "CONFIRMED"),
                    "dismissed": sum(1 for d in hitl_decisions.values() if d.get("action") == "DISMISSED"),
                    "escalated": sum(1 for d in hitl_decisions.values() if d.get("action") == "ESCALATED"),
                    "pending":   sum(1 for v in violations if v.get("rule_id") not in hitl_decisions),
                },
                "violations": violations,
                "explanations": explanations,
                "hitl_decisions": list(hitl_decisions.values()),
            }
            st.download_button(
                "⬇️ Download Compliance Report",
                data=json.dumps(report_data, indent=2, ensure_ascii=False),
                file_name=f"turgon_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                width="stretch",
            )
        else:
            st.caption("Run the pipeline first to generate a compliance report.")