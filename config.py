"""
config.py — Central configuration for Turgon.

All constants and environment loading live here.
Other modules import from this file; never import dotenv elsewhere.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env ─────────────────────────────────────────────────────────────────
load_dotenv()

# ── Base Paths ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
RULES_DIR = BASE_DIR / "rules"
UPLOADS_DIR = BASE_DIR / "uploads"

# Create directories if they don't exist
for _dir in [DATA_DIR, RULES_DIR, UPLOADS_DIR]:
    _dir.mkdir(exist_ok=True)

# ── OpenRouter / LLM ──────────────────────────────────────────────────────────
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

# Model to use via OpenRouter.
# IMPORTANT: prefix with 'openrouter/' so LiteLLM routes via OpenRouter's
# OpenAI-compatible API rather than trying a native provider SDK.
# Any OpenRouter model slug works — just prepend 'openrouter/'.
# Examples:
#   openrouter/google/gemini-2.0-flash-001
#   openrouter/anthropic/claude-3-haiku
#   openrouter/openai/gpt-4o-mini
DEFAULT_MODEL: str = os.getenv("TURGON_MODEL", "openrouter/z-ai/glm-4.5-air:free")

# CrewAI agent settings
AGENT_MAX_ITER: int = 15
AGENT_VERBOSE: bool = True

# ── DuckDB ─────────────────────────────────────────────────────────────────────
DUCKDB_PATH: Path = DATA_DIR / "aml.db"

# IBM AML dataset — place CSV files in the data/ directory.
# Download from: https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml
# Supported file names (script will try each in order):
AML_CSV_CANDIDATES: list[str] = [
    "HI-Small_Trans.csv",
    "HI-Medium_Trans.csv",
    "HI-Large_Trans.csv",
    "LI-Small_Trans.csv",
    "LI-Medium_Trans.csv",
    "LI-Large_Trans.csv",
]

# ── Rules Store ────────────────────────────────────────────────────────────────
RULES_JSON_PATH: Path = RULES_DIR / "policy_rules.json"

# ── Execution Sandbox ──────────────────────────────────────────────────────────
# Maximum rows returned from a single SQL violation query
MAX_VIOLATION_ROWS: int = 500

# Maximum rules to process in a single CrewAI run (0 = unlimited)
MAX_RULES_PER_RUN: int = 0

# Maximum rules the QueryEngineerAgent processes per batch
SQL_BATCH_SIZE: int = 10

# ── Validation ─────────────────────────────────────────────────────────────────
if not OPENROUTER_API_KEY:
    import warnings
    warnings.warn(
        "OPENROUTER_API_KEY is not set. "
        "Set it in your .env file before running the pipeline.",
        stacklevel=2,
    )


def get_llm():
    """
    Return a CrewAI LLM instance that routes through OpenRouter.

    Why CrewAI LLM instead of ChatOpenAI?
      CrewAI's Agent constructor calls crewai.utilities.llm_utils.create_llm()
      which inspects the object type. Passing a raw ChatOpenAI object causes it
      to re-wrap it through LiteLLM's provider detection, which sees 'google/'
      in the model name and tries to load the native Gemini SDK (not installed).

      Using CrewAI's own LLM class with the 'openrouter/' prefix tells LiteLLM
      to use the openrouter/ provider route -> OpenRouter's OpenAI-compatible API.
    """
    from crewai import LLM

    return LLM(
        model=DEFAULT_MODEL,             # e.g. openrouter/google/gemini-2.0-flash-001
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,    # https://openrouter.ai/api/v1
        temperature=0.0,                 # deterministic for compliance extraction
        max_tokens=4096,
        extra_headers={
            "HTTP-Referer": "https://github.com/turgon-engine",
            "X-Title": "Turgon Policy Engine",
        },
    )
