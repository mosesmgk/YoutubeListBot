#!/usr/bin/env python3
"""
YouTube Playlist Transcript Bot

Monitors a YouTube playlist for new videos and saves transcripts as Markdown files.
Already-processed videos are tracked in state.json and skipped on subsequent runs.

Usage:
    python3 main.py

Setup:
    1. Copy .env.example to .env and fill in your YOUTUBE_API_KEY and PLAYLIST_ID
    2. pip install -r requirements.txt
    3. Run the script; transcripts are saved to the transcripts/ directory

To run on a schedule (hourly via cron):
    0 * * * * cd /path/to/YoutubeListBot && /usr/bin/python3 main.py >> /var/log/ytbot.log 2>&1
"""
import logging
import sys

import config
from config import PLAYLIST_ID, LANGUAGES
from youtube_api import iter_playlist_videos
from transcript_fetcher import fetch_transcript, RequestBlocked, IpBlocked
from markdown_writer import write_transcript
from state_manager import load_state, save_state, mark_processed, is_processed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> int:
    try:
        config.validate()
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        return 1

    state = load_state()
    new_count = 0
    skipped_count = 0
    failed_count = 0

    try:
        for video in iter_playlist_videos(PLAYLIST_ID):
            video_id = video["video_id"]

            if is_processed(state, video_id):
                logger.debug("Already processed, skipping: %s (%s)", video["title"], video_id)
                skipped_count += 1
                continue

            logger.info("Processing: %s (%s)", video["title"], video_id)

            try:
                result = fetch_transcript(video_id, LANGUAGES)
            except (RequestBlocked, IpBlocked):
                logger.error(
                    "Run aborted due to IP/request block after processing %d new video(s).",
                    new_count,
                )
                save_state(state)
                return 1

            if result is None:
                logger.warning(
                    "No transcript available for: %s (%s). Skipping.",
                    video["title"], video_id,
                )
                failed_count += 1
                continue

            rel_path = write_transcript(video, result)
            mark_processed(
                state,
                video_id=video_id,
                title=video["title"],
                markdown_file=rel_path,
                language_code=result.language_code,
                is_generated=result.is_generated,
            )
            save_state(state)
            new_count += 1

    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        save_state(state)
        return 1

    logger.info(
        "Run complete. New: %d | Skipped (already done): %d | Failed (no transcript): %d",
        new_count, skipped_count, failed_count,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
