#!/usr/bin/env python3
"""Download the highest-bitrate MP4 from a public X/Twitter post."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
import urllib.parse
import urllib.request


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

VARIANT_RE = re.compile(
    r'bitrate:(?P<bitrate>\d+),content_type:"video/mp4",url:"(?P<url>https://video\.twimg\.com/[^"]+\.mp4[^"]*)"'
)
STATUS_ID_RE = re.compile(r"/status/(\d+)")


def normalize_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc not in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
        raise ValueError("URL must be an x.com or twitter.com post URL")
    cleaned = parsed._replace(query="", fragment="")
    return urllib.parse.urlunparse(cleaned)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def find_best_variant(html: str) -> tuple[int, str]:
    matches = []
    for match in VARIANT_RE.finditer(html):
        bitrate = int(match.group("bitrate"))
        url = match.group("url").encode("utf-8").decode("unicode_escape")
        matches.append((bitrate, url))
    if not matches:
        raise RuntimeError("No MP4 variants found in the post HTML")
    return max(matches, key=lambda item: item[0])


def infer_default_output(url: str) -> pathlib.Path:
    match = STATUS_ID_RE.search(url)
    status_id = match.group(1) if match else "video"
    return pathlib.Path(f"x-post-{status_id}.mp4")


def download_file(url: str, output_path: pathlib.Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response, output_path.open("wb") as handle:
        handle.write(response.read())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download the highest-bitrate MP4 from a public X/Twitter post."
    )
    parser.add_argument("url", help="X/Twitter post URL")
    parser.add_argument(
        "--output",
        help="Output MP4 path. Defaults to ./x-post-<status-id>.mp4",
    )
    args = parser.parse_args()

    post_url = normalize_url(args.url)
    output_path = pathlib.Path(args.output) if args.output else infer_default_output(post_url)

    html = fetch_text(post_url)
    bitrate, media_url = find_best_variant(html)
    download_file(media_url, output_path)

    print(f"saved={output_path.resolve()}")
    print(f"bitrate={bitrate}")
    print(f"source={media_url}")
    print(f"bytes={output_path.stat().st_size}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI failure path
        print(f"error={exc}", file=sys.stderr)
        raise SystemExit(1)
