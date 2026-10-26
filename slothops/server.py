import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import STATIC_DIR, DEFAULT_MODEL, OLLAMA_BASE_URL
from .engine.llm_client import LLMClient
from .engine.summarizer import MorningBriefEngine
from .engine.sorter import ClutterSorter
from .engine.winddown import WindDownEngine

app = FastAPI(
    title="SlothOps API",
    description="The slow, steady, and utterly chill local AI agent for automated de-cluttering and daily wind-downs.",
    version="0.1.0"
)

# Core engine singletons
llm_client = LLMClient()
brief_engine = MorningBriefEngine(llm_client)
sorter_engine = ClutterSorter(llm_client)
winddown_engine = WindDownEngine(llm_client)

# Pydantic Request Models
class BriefRequest(BaseModel):
    notes: str
    model: Optional[str] = None

class ScanRequest(BaseModel):
    directory: str

class ExecuteTidyRequest(BaseModel):
    items: List[Dict[str, Any]]

class WindDownRequest(BaseModel):
    accomplishments: str
    model: Optional[str] = None

# Routes
@app.get("/api/status")
def get_status():
    status = llm_client.check_availability()
    return {
        "status": "online",
        "llm": status,
        "features": {
            "morning_brief": True,
            "clutter_sorter": True,
            "wind_down_companion": True,
            "procedural_soundscapes": True
        }
    }

@app.post("/api/brief")
def create_brief(req: BriefRequest):
    if req.model:
        llm_client.model = req.model
    return brief_engine.generate_brief(req.notes)

@app.post("/api/tidy/scan")
def scan_clutter(req: ScanRequest):
    result = sorter_engine.scan_directory(req.directory)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/tidy/execute")
def execute_tidy(req: ExecuteTidyRequest):
    return sorter_engine.execute_tidy(req.items)

@app.post("/api/tidy/undo")
def undo_tidy():
    return sorter_engine.undo_last()

@app.post("/api/winddown")
def generate_winddown(req: WindDownRequest):
    if req.model:
        llm_client.model = req.model
    return winddown_engine.generate_winddown(req.accomplishments)

# Mount web frontend
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "SlothOps API is running. Web UI not found in static directory."}
