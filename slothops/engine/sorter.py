import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from .llm_client import LLMClient

CATEGORY_RULES = {
    "Finance_Invoices": {
        "keywords": ["invoice", "receipt", "tax", "bill", "salary", "expense", "payment", "bank", "statement"],
        "extensions": [".pdf", ".csv", ".xlsx", ".txt", ".png", ".jpg"]
    },
    "Code_and_Dev": {
        "keywords": ["script", "test", "patch", "config", "src", "snippet", "api", "debug"],
        "extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json", ".yaml", ".yml", ".sh", ".rs", ".go", ".c", ".cpp", ".sql"]
    },
    "Documents": {
        "keywords": ["doc", "paper", "report", "notes", "summary", "contract", "guide", "manual", "draft"],
        "extensions": [".pdf", ".docx", ".doc", ".odt", ".rtf", ".txt", ".md"]
    },
    "Data_and_Sheets": {
        "keywords": ["dataset", "export", "data", "metrics", "analytics", "table"],
        "extensions": [".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".sqlite", ".db"]
    },
    "Media_and_Design": {
        "keywords": ["screenshot", "screen", "capture", "photo", "img", "recording", "banner", "logo", "wallpaper"],
        "extensions": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".mp4", ".mov", ".mkv", ".mp3", ".wav"]
    },
    "Archives_and_Installers": {
        "keywords": ["setup", "install", "archive", "pack", "dist", "backup"],
        "extensions": [".zip", ".tar", ".gz", ".tar.gz", ".rar", ".7z", ".exe", ".msi", ".dmg", ".pkg", ".iso"]
    }
}

class ClutterSorter:
    """
    Automates file categorization and workspace de-cluttering.
    Provides safety with dry-run previews, conflict avoidance, and execution logging.
    """
    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.undo_stack: List[Dict[str, str]] = []

    def classify_file(self, filename: str, content_preview: str = "") -> str:
        lower_name = filename.lower()
        lower_content = content_preview.lower()
        ext = Path(filename).suffix.lower()

        # 1. Financial check: files with financial keywords
        for kw in CATEGORY_RULES["Finance_Invoices"]["keywords"]:
            if kw in lower_name or kw in lower_content:
                return "Finance_Invoices"

        # 2. Strict code extensions
        if ext in CATEGORY_RULES["Code_and_Dev"]["extensions"]:
            return "Code_and_Dev"

        # 3. Media & Design extensions
        if ext in CATEGORY_RULES["Media_and_Design"]["extensions"]:
            return "Media_and_Design"

        # 4. Data & Spreadsheets extensions
        if ext in CATEGORY_RULES["Data_and_Sheets"]["extensions"]:
            return "Data_and_Sheets"

        # 5. Archive & Installer extensions
        if ext in CATEGORY_RULES["Archives_and_Installers"]["extensions"]:
            return "Archives_and_Installers"

        # 6. Document extensions
        if ext in CATEGORY_RULES["Documents"]["extensions"]:
            return "Documents"

        # 7. Fallback to keyword matching across remaining categories
        for category, rules in CATEGORY_RULES.items():
            if any(kw in lower_name for kw in rules["keywords"]):
                return category

        return "Miscellaneous"

    def scan_directory(self, target_dir: str) -> Dict[str, Any]:
        path = Path(target_dir).resolve()
        if not path.exists() or not path.is_dir():
            return {"error": f"Directory not found: {target_dir}", "items": []}

        items = []
        for entry in os.scandir(path):
            if entry.is_file() and not entry.name.startswith("."):
                content_sample = ""
                # Try reading first 256 bytes for text files
                try:
                    if entry.stat().st_size < 100_000:
                        with open(entry.path, "r", encoding="utf-8", errors="ignore") as f:
                            content_sample = f.read(512)
                except Exception:
                    pass

                target_category = self.classify_file(entry.name, content_sample)
                items.append({
                    "original_path": entry.path,
                    "filename": entry.name,
                    "size_bytes": entry.stat().st_size,
                    "suggested_category": target_category,
                    "suggested_destination": str(path / target_category / entry.name)
                })

        return {
            "source_dir": str(path),
            "total_files": len(items),
            "items": items
        }

    def execute_tidy(self, items: List[Dict[str, str]]) -> Dict[str, Any]:
        moved_count = 0
        errors = []
        recent_moves = []

        for item in items:
            src = Path(item["original_path"])
            dest = Path(item["suggested_destination"])
            if not src.exists():
                continue

            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Handle destination conflicts safely
                final_dest = dest
                if final_dest.exists() and final_dest.resolve() != src.resolve():
                    stem = dest.stem
                    suffix = dest.suffix
                    counter = 1
                    while final_dest.exists():
                        final_dest = dest.parent / f"{stem}_{counter}{suffix}"
                        counter += 1

                shutil.move(str(src), str(final_dest))
                recent_moves.append({"from": str(src), "to": str(final_dest)})
                moved_count += 1
            except Exception as e:
                errors.append({"file": str(src), "error": str(e)})

        self.undo_stack.extend(recent_moves)
        return {
            "moved_count": moved_count,
            "errors": errors,
            "moves": recent_moves
        }

    def undo_last(self) -> Dict[str, Any]:
        if not self.undo_stack:
            return {"status": "empty", "restored": 0}

        restored = 0
        errors = []
        while self.undo_stack:
            move = self.undo_stack.pop()
            src = Path(move["to"])
            dest = Path(move["from"])
            try:
                if src.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dest))
                    restored += 1
            except Exception as e:
                errors.append({"file": str(src), "error": str(e)})

        return {"status": "ok", "restored": restored, "errors": errors}
