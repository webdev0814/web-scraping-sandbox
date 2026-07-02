---
name: video-extract
description: Extract video files from public X or Twitter post URLs and save them as local MP4 files. Use when a user wants the video from a post downloaded, converted into a standalone `.mp4`, saved to a specific folder such as Downloads, or published as a reusable extraction workflow.
---

# Video Extract

Extract the highest-quality MP4 variant from a public X or Twitter post and save it to disk.
Prefer the bundled script for reliability instead of reimplementing the scrape logic in-line.

## Quick Start

1. Choose an output path.
2. Run `scripts/extract_x_video.py` with the post URL.
3. Verify the saved file exists and report the final path.

Use the bundled workspace Python when `python` is missing from `PATH`. In Codex desktop threads, call `load_workspace_dependencies` and use the reported Python executable.

Example:

```powershell
& "C:\path\to\python.exe" "...\scripts\extract_x_video.py" `
  "https://x.com/user/status/1234567890" `
  --output "$env:USERPROFILE\Downloads\x-post-1234567890.mp4"
```

## Workflow

### 1. Normalize the request

- Accept `x.com` and `twitter.com` post URLs.
- Default to the user's requested destination. If none is given, prefer `Downloads`.
- Name the file `x-post-<status-id>.mp4` unless the user asks for a different filename.

### 2. Run the script

Pass the post URL and an explicit `--output` path.
The script extracts MP4 variants from the public page HTML, chooses the highest bitrate, and downloads that asset directly.

### 3. Verify the result

- Confirm the file exists.
- Report the absolute path.
- If useful, report file size or resolution inferred from the selected variant URL.

## Failure Modes

- If the post is protected, deleted, geo-restricted, or no longer exposes public variant URLs, stop and say the media could not be extracted from the public page.
- If the user asks for audio-only, this skill is not the best fit; extract the MP4 first, then convert separately if needed.
- If multiple videos are present in one post, inspect the page data carefully before assuming a single result. The bundled script currently targets the first video entity found on the page.

## Resources

### `scripts/extract_x_video.py`

- Inputs: post URL, optional output path
- Output: downloaded `.mp4`
- Behavior: picks the highest bitrate MP4 variant exposed by the public post HTML
