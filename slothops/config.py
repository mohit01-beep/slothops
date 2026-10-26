import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "web"
DATA_DIR = BASE_DIR / "data"

# LLM Settings (Open-source local inference)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("SLOTHOPS_MODEL", "llama3.2")
FALLBACK_ENABLED = os.getenv("SLOTHOPS_FALLBACK", "true").lower() in ("true", "1", "yes")

# Server settings
HOST = os.getenv("SLOTHOPS_HOST", "127.0.0.1")
PORT = int(os.getenv("SLOTHOPS_PORT", 8765))
