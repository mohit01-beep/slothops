import re
import json
import random
from typing import Dict, Any, List
from .llm_client import LLMClient

SLOTH_WISDOMS = [
    "You don't have to sprint when a steady stroll gets you there with lower cortisol.",
    "A tree doesn't rush its fruit; why should you rush another git commit?",
    "Energy saved today is focus compounded tomorrow. Breathe easy.",
    "Doing three things well beats starting twenty things in a panic.",
    "The art of laziness isn't avoiding work—it's ruthlessly automating the mundane.",
    "Nature never hurries, yet everything gets accomplished.",
    "Close two tabs for every one you open. Your RAM and your mind will thank you."
]

class MorningBriefEngine:
    """
    Synthesizes messy unstructured daily logs, to-dos, and brain dumps into a calm,
    structured 3-point briefing using local open-weight AI.
    """
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate_brief(self, raw_notes: str) -> Dict[str, Any]:
        raw_notes = raw_notes.strip()
        if not raw_notes:
            return {
                "source": "empty",
                "high_impact": ["Breathe and stretch your shoulders."],
                "safe_to_ignore": ["Everything else until you've had coffee or tea."],
                "wisdom": random.choice(SLOTH_WISDOMS),
                "time_saved_minutes": 15,
                "engine_used": "Sloth Built-in Defaults"
            }

        # Check local LLM first
        system_prompt = (
            "You are SlothOps, a calm, deeply pragmatic, open-source AI assistant. "
            "Your philosophy is 'Slow and Steady'. You cut through hustle-culture noise. "
            "Analyze the user's messy notes and return a strictly valid JSON object with keys: "
            "'high_impact' (array of 1-3 critical tasks that genuinely move the needle), "
            "'safe_to_ignore' (array of 1-3 tasks that can wait or be dropped), "
            "'wisdom' (a calming 1-sentence sloth-inspired thought), "
            "'time_saved_minutes' (estimated integer minutes saved by not stressing over low-value clutter)."
        )

        prompt = f"Here are my raw thoughts and messy tasks for today:\n\n{raw_notes}\n\nRespond ONLY in JSON format."
        
        llm_response = self.llm.generate(prompt=prompt, system_prompt=system_prompt, format_json=True)
        if llm_response:
            try:
                # Clean markdown blocks if any
                clean_json = re.sub(r"^```(?:json)?\s*", "", llm_response.strip())
                clean_json = re.sub(r"\s*```$", "", clean_json)
                parsed = json.loads(clean_json)
                parsed["engine_used"] = f"Local LLM ({self.llm.model})"
                return parsed
            except Exception:
                pass

        # Fallback heuristic engine
        return self._heuristic_brief(raw_notes)

    def _heuristic_brief(self, text: str) -> Dict[str, Any]:
        """Intelligent local heuristic parser if no LLM is currently loaded."""
        lines = [line.strip("- *0123456789.[]\t ") for line in text.splitlines() if line.strip()]
        
        urgent_keywords = ["urgent", "today", "fix", "deadline", "ship", "bug", "deploy", "asap", "prod", "critical", "submit", "release"]
        low_priority_keywords = ["maybe", "later", "someday", "clean", "research", "explore", "consider", "look into", "read", "update docs"]

        high_impact = []
        safe_to_ignore = []

        for line in lines:
            lower = line.lower()
            if any(k in lower for k in urgent_keywords):
                high_impact.append(line)
            elif any(k in lower for k in low_priority_keywords):
                safe_to_ignore.append(line)

        # Distribute remaining lines if buckets are empty
        for line in lines:
            if line not in high_impact and line not in safe_to_ignore:
                if len(high_impact) < 3:
                    high_impact.append(line)
                else:
                    safe_to_ignore.append(line)

        if not high_impact:
            high_impact = ["Review your primary objective calmly", "Take one focused step forward"]
        if not safe_to_ignore:
            safe_to_ignore = ["Endless slack/email refreshes", "Refactoring code that already works well"]

        return {
            "high_impact": high_impact[:3],
            "safe_to_ignore": safe_to_ignore[:3],
            "wisdom": random.choice(SLOTH_WISDOMS),
            "time_saved_minutes": max(15, len(lines) * 4),
            "engine_used": "SlothOps Local Heuristic Engine (Offline Fallback)"
        }
