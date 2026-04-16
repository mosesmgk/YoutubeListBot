import logging
from typing import Iterator

from googleapiclient.discovery import build

from config import YOUTUBE_API_KEY

logger = logging.getLogger(__name__)


def _build_service():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def iter_playlist_videos(playlist_id: str) -> Iterator[dict]:
    """Yield one dict per video in the playlist, handling pagination automatically.

    Yielded dict keys: video_id, title, published_at, channel, url
    Deleted/private videos are skipped silently.
    """
    service = _build_service()
    page_token = None

    while True:
        request = service.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=page_token,
        )
        response = request.execute()

        for item in response.get("items", []):
            snippet = item.get("snippet")
            if not snippet:
                continue
            resource = snippet.get("resourceId", {})
            if resource.get("kind") != "youtube#video":
                continue
            video_id = resource.get("videoId")
            if not video_id:
                continue

            yield {
                "video_id": video_id,
                "title": snippet.get("title", "Untitled"),
                "published_at": snippet.get("publishedAt", ""),
                "channel": snippet.get("videoOwnerChannelTitle", "Unknown"),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }

        page_token = response.get("nextPageToken")
        if not page_token:
            break
