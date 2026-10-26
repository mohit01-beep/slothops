import json
import re
import random
from typing import Dict, Any, List
from .llm_client import LLMClient

SOOTHING_THEMES = [
    {"name": "Rain on Canopy", "type": "rain", "frequency": 180, "description": "Gentle drops falling on broad jungle leaves."},
    {"name": "Warm Lo-Fi Drone", "type": "drone", "frequency": 110, "description": "Analog soothing sine waves in relaxing A-432Hz tuning."},
    {"name": "Sloth Forest Night", "type": "forest", "frequency": 240, "description": "Distant night wind and rustling leaves."}
]

class WindDownEngine:
    """
    Helps developers transition out of work mode without lingering anxiety.
    Celebrates what got done and gently dismisses unfinished tasks until tomorrow.
    """
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate_winddown(self, accomplishments: str = "") -> Dict[str, Any]:
        accomplishments = accomplishments.strip()

        # Prompt local LLM if active
        if accomplishments:
            system_prompt = (
                "You are SlothOps, an evening wind-down assistant for developers and builders. "
                "Your goal is to validate what the user accomplished today and give them explicit, "
                "guilt-free permission to shut down and relax. Be warm, humorous, and calming. "
                "Return a JSON object with: 'recap' (a warm 2-sentence summary of wins), "
                "'permission_to_rest' (a reassuring sentence releasing today's stress), "
                "'tomorrow_mantra' (a short 5-word calming mantra)."
            )
            prompt = f"Here is what I touched/completed today:\n{accomplishments}\n\nRespond strictly in JSON."
            llm_res = self.llm.generate(prompt=prompt, system_prompt=system_prompt, format_json=True)
            if llm_res:
                try:
                    clean = re.sub(r"^```(?:json)?\s*", "", llm_res.strip())
                    clean = re.sub(r"\s*```$", "", clean)
                    parsed = json.loads(clean)
                    parsed["soundscape"] = random.choice(SOOTHING_THEMES)
                    parsed["engine_used"] = f"Local LLM ({self.llm.model})"
                    return parsed
                except Exception:
                    pass

        # Heuristic default
        wins = [line.strip("- *0123456789. ") for line in accomplishments.splitlines() if line.strip()]
        if not wins:
            wins = ["Kept your momentum going", "Navigated through another busy day"]

        return {
            "recap": f"You made real progress today across {len(wins)} key area{'s' if len(wins) > 1 else ''}. Every small step counts.",
            "permission_to_rest": "The codebase will still be here tomorrow. You have earned a complete mental pause.",
            "tomorrow_mantra": "Slow, steady, and unstoppable.",
            "soundscape": random.choice(SOOTHING_THEMES),
            "engine_used": "SlothOps Built-in Wind-Down Engine"
        }
