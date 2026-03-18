---
name: youtube-search
description: Extract transcripts and metadata from YouTube using either a search query or a direct YouTube video URL. Use when the user wants fresh YouTube research input, transcript files, video metadata, or a source-ingestion step before NotebookLM.
---

# YouTube Search

Use the deterministic runner:

```powershell
py scripts/run_youtube_ingest.py "<query-or-url>" --max-results 5
```

## Rules

- Prefer a direct YouTube URL when the user already knows the exact video.
- Use a search query when the user wants discovery across multiple videos.
- Return the transcript directory, transcript files, captured videos, and any warnings.
- If `yt-dlp` is missing, run `py scripts/setup.py` first.

## Output contract

The script prints JSON with:

- `mode`
- `transcript_dir`
- `transcript_files`
- `warnings`
- `videos`
