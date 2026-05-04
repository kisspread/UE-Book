"""Pipeline configuration.

Local overrides go in config.local.py (git-ignored).
See config.local.example.py for template.
"""
import os

# Paths — override in config.local.py
UE_SOURCE = "/path/to/UnrealEngine"       # UE 源码根目录
GIT_MAIN_REPO = "/path/to/UnrealEngine"   # Git 主仓库（worktree 结构时与 UE_SOURCE 不同）
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_PATH = os.path.join(PROJECT_DIR, "harness.md")
PLUGINS_INDEX = os.path.join(PROJECT_DIR, "plugins-index.json")

# LLM — any OpenAI-compatible provider
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

# Pipeline
BATCH_SIZE = 3  # parallel plugins per batch
MAX_RETRIES = 2

# ── Load local overrides (git-ignored) ──
try:
    from .config_local import *  # noqa: F401,F403
except ImportError:
    pass
