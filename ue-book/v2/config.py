"""v2 Pipeline configuration — GitHub Actions + local dev."""
import os

# ── Paths ──
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_PATH = os.path.join(PROJECT_DIR, "harness.md")
MANIFEST_PATH = os.path.join(PROJECT_DIR, "manifest.json")

# ── GitHub ──
GH_REPO = "EpicGames/UnrealEngine"
GH_BRANCH_DEFAULT = "release"  # fallback

# ── LLM ──
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

# ── Pipeline ──
BATCH_SIZE = 3
MAX_RETRIES = 2

# ── Load local overrides (git-ignored) ──
try:
    from .config_local import *  # noqa: F401,F403
except ImportError:
    pass
