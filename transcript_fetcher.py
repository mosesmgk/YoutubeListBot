import logging
from dataclasses import dataclass
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    AgeRestricted,
    VideoUnplayable,
    RequestBlocked,
    IpBlocked,
)

logger = logging.getLogger(__name__)


@dataclass
class TranscriptResult:
    video_id: str
    language_code: str
    is_generated: bool
    snippets: list


def fetch_transcript(
    video_id: str,
    preferred_languages: list[str],
) -> Optional[TranscriptResult]:
    """Fetch transcript for a video with language fallback and graceful error handling.

    Returns None if no transcript is available (caller should skip the video).
    Re-raises RequestBlocked/IpBlocked so the caller can abort the entire run.
    """
    ytt_api = YouTubeTranscriptApi()

    try:
        transcript_list = ytt_api.list(video_id)
    except TranscriptsDisabled:
        logger.warning("[%s] Transcripts are disabled for this video.", video_id)
        return None
    except VideoUnavailable:
        logger.warning("[%s] Video is unavailable.", video_id)
        return None
    except AgeRestricted:
        logger.warning("[%s] Video is age-restricted; cannot fetch transcript.", video_id)
        return None
    except VideoUnplayable:
        logger.warning("[%s] Video is unplayable.", video_id)
        return None
    except (RequestBlocked, IpBlocked) as e:
        logger.error("IP/request blocked by YouTube. Details: %s", e)
        raise

    transcript_obj = None
    try:
        transcript_obj = transcript_list.find_transcript(preferred_languages)
    except NoTranscriptFound:
        available = list(transcript_list)
        if not available:
            logger.warning("[%s] No transcripts available at all.", video_id)
            return None
        transcript_obj = available[0]
        logger.info(
            "[%s] No preferred-language transcript found; using '%s' (%s).",
            video_id,
            transcript_obj.language_code,
            "generated" if transcript_obj.is_generated else "manual",
        )

    fetched = transcript_obj.fetch()
    return TranscriptResult(
        video_id=video_id,
        language_code=transcript_obj.language_code,
        is_generated=transcript_obj.is_generated,
        snippets=list(fetched),
    )
