# YoutubeListBot

Monitors a YouTube playlist and saves transcripts of each video as Markdown files. Run it on a schedule to automatically capture new additions to your playlist.

## How it works

1. Fetches all videos from your target playlist via the YouTube Data API
2. Skips any videos already transcribed (tracked in `state.json`)
3. Pulls captions/auto-generated subtitles for each new video
4. Saves a `.md` file per video in a `transcripts/` folder

Each transcript looks like this:

```markdown
# Video Title

| Field | Value |
|---|---|
| URL | [https://www.youtube.com/watch?v=...](https://...) |
| Published | 2024-01-15T00:00:00Z |
| Channel | Channel Name |
| Transcribed | 2026-04-16 10:30 UTC |
| Transcript Language | en (auto-generated) |

## Transcript

**[00:00]** First words spoken in the video...

**[00:05]** More words...
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a YouTube Data API key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services → Library** and enable the **YouTube Data API v3**
4. Go to **APIs & Services → Credentials** and click **Create Credentials → API key**
5. Copy the generated API key

### 3. Find your playlist ID

1. Open your playlist on YouTube
2. Look at the URL — it will look like:
   ```
   https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. Copy the value after `list=` — that is your playlist ID (starts with `PL`)

### 4. Create your `.env` file

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set your API key and playlist ID:

```
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
PLAYLIST_ID=PLxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> `.env` is gitignored and will never be committed.

---

## Usage

### Run once

```bash
python3 main.py
```

The bot will process all new videos in your playlist and save transcripts to the `transcripts/` folder. Re-running it will skip already-processed videos.

### Run on a schedule (optional)

To check for new videos automatically, add a cron job (`crontab -e`):

```cron
# Run every hour
0 * * * * cd /path/to/YoutubeListBot && /usr/bin/python3 main.py >> /var/log/ytbot.log 2>&1
```

---

## Output

Transcripts are saved to `transcripts/` with filenames based on the video title:

```
transcripts/
├── How_to_Learn_Anything_Fast.md
├── The_Future_of_AI.md
└── ...
```

The `transcripts/` folder and `state.json` are gitignored so they stay local to your machine.

---

## Notes

- Videos with transcripts **disabled** or set to **private/unavailable** are skipped with a warning and retried on the next run
- If no English transcript exists, the bot falls back to whatever language is available
- The bot processes only **new** videos on each run — already-transcribed videos are never re-processed
