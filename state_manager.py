import json
import os
from datetime import datetime, timezone
from typing import Any

from config import STATE_FILE


def load_state() -> dict[str, Any]:
    if not os.path.exists(STATE_FILE):
        return {"processed": {}}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict[str, Any]) -> None:
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    os.replace(tmp, STATE_FILE)


def mark_processed(
    state: dict[str, Any],
    video_id: str,
    title: str,
    markdown_file: str,
    language_code: str,
    is_generated: bool,
) -> None:
    state["processed"][video_id] = {
        "title": title,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "markdown_file": markdown_file,
        "language_code": language_code,
        "is_generated": is_generated,
    }


def is_processed(state: dict[str, Any], video_id: str) -> bool:
    return video_id in state["processed"]
