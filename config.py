import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
PLAYLIST_ID: str = os.getenv("PLAYLIST_ID", "")
TRANSCRIPTS_DIR: str = os.getenv("TRANSCRIPTS_DIR", "transcripts")
STATE_FILE: str = os.getenv("STATE_FILE", "state.json")
LANGUAGES: list[str] = ["en", "en-US", "en-GB"]


def validate() -> None:
    missing = [k for k, v in {"YOUTUBE_API_KEY": YOUTUBE_API_KEY,
                               "PLAYLIST_ID": PLAYLIST_ID}.items() if not v]
    if missing:
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")
