import os
import logging
from datetime import datetime, timezone

from transcript_fetcher import TranscriptResult
from utils import seconds_to_mmss, sanitize_filename
from config import TRANSCRIPTS_DIR

logger = logging.getLogger(__name__)


def _render_markdown(video: dict, result: TranscriptResult) -> str:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lang_label = result.language_code
    if result.is_generated:
        lang_label += " (auto-generated)"

    url = video["url"]
    lines = [
        f"# {video['title']}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| URL | [{url}]({url}) |",
        f"| Published | {video['published_at']} |",
        f"| Channel | {video['channel']} |",
        f"| Transcribed | {now_utc} |",
        f"| Transcript Language | {lang_label} |",
        "",
        "## Transcript",
        "",
    ]

    for snippet in result.snippets:
        ts = seconds_to_mmss(snippet.start)
        text = snippet.text.strip().replace("\n", " ")
        lines.append(f"**[{ts}]** {text}")
        lines.append("")

    return "\n".join(lines)


def write_transcript(video: dict, result: TranscriptResult) -> str:
    """Write a markdown transcript file. Returns the relative file path."""
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    base_name = sanitize_filename(video["title"])
    rel_path = os.path.join(TRANSCRIPTS_DIR, f"{base_name}.md")

    if os.path.exists(rel_path):
        rel_path = os.path.join(TRANSCRIPTS_DIR, f"{base_name}_{video['video_id']}.md")

    content = _render_markdown(video, result)
    with open(rel_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("Written: %s", rel_path)
    return rel_path
