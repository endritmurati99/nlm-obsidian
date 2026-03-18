---
name: youtube-search
description: Use when searching YouTube for videos and extracting transcripts. Triggers when the user wants to research a topic using YouTube, find video transcripts, gather video metadata, or feed YouTube content into a research pipeline. Use this skill even if the user just says "search YouTube for X" or "find videos about X".
---

# YouTube Search & Transcript Extraction

Searches YouTube and extracts transcripts using `yt-dlp`. Designed as the data-ingestion module of the research pipeline — its output feeds directly into NotebookLM.

## Prerequisites

`yt-dlp` must be installed: `pip install yt-dlp`

## Inputs

| Parameter | Description | Example |
|-----------|-------------|---------|
| `query` | Search terms | `"Claude Code MCP"` |
| `max_results` | Number of videos (default: 5, max: 20) | `10` |
| `output_dir` | Where to save transcripts | `tmp/transcripts/` |

## Execution Steps

### Step 1 — Search and collect metadata

```bash
yt-dlp "ytsearch{max_results}:{query}" \
  --skip-download \
  --print "%(id)s\t%(title)s\t%(webpage_url)s\t%(view_count)s\t%(upload_date)s" \
  --no-playlist \
  > {output_dir}/metadata.tsv
```

### Step 2 — Download auto-generated transcripts

```bash
yt-dlp "ytsearch{max_results}:{query}" \
  --skip-download \
  --write-auto-sub \
  --write-sub \
  --sub-lang en \
  --sub-format ttml \
  --convert-subs srt \
  --no-playlist \
  -o "{output_dir}/%(id)s.%(ext)s"
```

### Step 3 — Clean and consolidate transcripts

For each `.srt` file, strip timestamps and deduplicate consecutive lines to produce clean `.txt` files. Use this Python snippet:

```python
import re, pathlib

def clean_srt(srt_path: str) -> str:
    text = pathlib.Path(srt_path).read_text(encoding="utf-8", errors="ignore")
    # Remove sequence numbers and timestamps
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', text)
    # Deduplicate consecutive identical lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    deduped = [lines[0]] + [l for i, l in enumerate(lines[1:]) if l != lines[i]]
    return ' '.join(deduped)
```

Save clean transcripts as `{output_dir}/{video_id}.txt`.

### Step 4 — Return structured result

Return a summary to the caller:

```
YOUTUBE_SEARCH_RESULT
query: {query}
videos_found: {n}
transcript_dir: {output_dir}
files: [{video_id}.txt, ...]
metadata: {output_dir}/metadata.tsv
```

## Output Structure

```
tmp/transcripts/
├── metadata.tsv          # id, title, url, views, date
├── {video_id}.txt        # clean transcript per video
└── {video_id}.txt
```

## Common Issues

| Problem | Fix |
|---------|-----|
| `yt-dlp: command not found` | Run `pip install yt-dlp` or `pip install -U yt-dlp` |
| No transcripts available | Some videos disable captions — skip those and continue |
| Transcripts in wrong language | Add `--sub-lang en,en-US,en-GB` to the download command |
| Rate limiting | Add `--sleep-interval 2 --max-sleep-interval 5` |
