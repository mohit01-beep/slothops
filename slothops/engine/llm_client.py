import json
import logging
from typing import Optional, Dict, Any, List
import httpx
from ..config import OLLAMA_BASE_URL, DEFAULT_MODEL

logger = logging.getLogger("slothops.llm")

class LLMClient:
    """
    Client for interacting with local open-weight models (via Ollama or OpenAI-compatible local APIs).
    Falls back cleanly to built-in semantic heuristics if no local model runner is detected.
    """
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = DEFAULT_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._is_available: Optional[bool] = None

    def check_availability(self) -> Dict[str, Any]:
        """Check if local Ollama or OpenAI-compatible endpoint is available and list models."""
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    self._is_available = True
                    return {
                        "available": True,
                        "provider": "Ollama (Local Open-Source)",
                        "endpoint": self.base_url,
                        "models": models,
                        "active_model": self.model if self.model in models or not models else models[0]
                    }
        except Exception:
            pass

        # Try OpenAI-compatible local endpoint (e.g. LM Studio, LocalAI)
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/v1/models")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("id", "") for m in data.get("data", [])]
                    self._is_available = True
                    return {
                        "available": True,
                        "provider": "Local OpenAI-Compatible (vLLM / LM Studio)",
                        "endpoint": self.base_url,
                        "models": models,
                        "active_model": self.model if self.model in models or not models else (models[0] if models else self.model)
                    }
        except Exception:
            pass

        self._is_available = False
        return {
            "available": False,
            "provider": "SlothOps Built-in Local Heuristic Engine (Zero-Config Fallback)",
            "endpoint": self.base_url,
            "models": ["sloth-built-in-heuristic"],
            "active_model": "sloth-built-in-heuristic"
        }

    def generate(self, prompt: str, system_prompt: Optional[str] = None, format_json: bool = False) -> str:
        """
        Generate completion using local Ollama model if reachable, otherwise return None.
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
                if system_prompt:
                    payload["system"] = system_prompt
                if format_json:
                    payload["format"] = "json"

                res = client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
        except Exception as e:
            logger.debug(f"Local LLM call failed or timed out: {e}")
        return ""
