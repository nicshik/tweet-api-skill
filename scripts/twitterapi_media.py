#!/usr/bin/env python3
"""Download tweet video media from supported X/Twitter API provider data."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from twitterapi_client import (
    TWITTERAPI_IO_PROVIDER,
    XQUIK_PROVIDER,
    build_ssl_context,
    extract_tweet_id,
    get_api_key,
    normalize_api_provider,
    provider_source_name,
    request_json,
)


ALLOWED_MEDIA_HOSTS = {"video.twimg.com"}
BUFFER_SIZE = 1024 * 1024
RESOLUTION_RE = re.compile(r"/(\d+)x(\d+)/")
USER_AGENT = "tweet-api-skill/0.4.3"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download the best MP4 video media from a tweet via a provider."
    )
    parser.add_argument("tweet", nargs="?", help="Tweet URL or raw tweet id.")
    parser.add_argument(
        "--input",
        dest="input_value",
        help="Tweet URL or raw tweet id. Alternative to the positional argument.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory for downloaded media files. Default: current directory.",
    )
    parser.add_argument(
        "--filename",
        help="Output filename. Only valid when exactly one video file is selected.",
    )
    parser.add_argument(
        "--first",
        action="store_true",
        help="Download only the first video media item if a tweet has several.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files instead of failing.",
    )
    parser.add_argument(
        "--api-key",
        help="Optional override. Prefer TWITTERAPI_IO_KEY or XQUIK_API_KEY env var.",
    )
    parser.add_argument(
        "--api-provider",
        choices=(TWITTERAPI_IO_PROVIDER, XQUIK_PROVIDER),
        help="API provider. Defaults to X_API_PROVIDER, API_PROVIDER, or twitterapi_io.",
    )
    return parser.parse_args()


def requested_input(args: argparse.Namespace) -> str:
    values = [value for value in (args.tweet, args.input_value) if value]
    if not values:
        raise ValueError("Pass a tweet URL or raw tweet id.")
    if len(values) > 1 and values[0] != values[1]:
        raise ValueError("Pass the tweet input either positionally or via --input, not both.")
    return values[0]


def fetch_tweet(
    tweet_id: str,
    api_key: str,
    api_provider: str = TWITTERAPI_IO_PROVIDER,
) -> dict[str, Any]:
    api_provider = normalize_api_provider(api_provider)
    if api_provider == XQUIK_PROVIDER:
        payload = request_json(
            method="GET",
            path="/x/tweets",
            query={"ids": tweet_id},
            api_key=api_key,
            api_provider=api_provider,
        )
        tweets = payload.get("tweets") or []
        if tweets and isinstance(tweets[0], dict):
            return tweets[0]
        raise RuntimeError(payload.get("message") or "Tweet not found")

    payload = request_json(
        method="GET",
        path="/twitter/tweets",
        query={"tweet_ids": tweet_id},
        api_key=api_key,
        api_provider=api_provider,
    )
    tweets = payload.get("tweets") or []
    if payload.get("status") == "success" and tweets:
        tweet = tweets[0]
        if isinstance(tweet, dict):
            return tweet
    raise RuntimeError(payload.get("message") or "Tweet not found")


def media_items(tweet: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    top_level_media = tweet.get("media")
    if isinstance(top_level_media, list):
        for item in top_level_media:
            if not isinstance(item, dict):
                continue
            item_key = str(
                item.get("media_key")
                or item.get("mediaKey")
                or item.get("id_str")
                or item.get("url")
                or item.get("mediaUrl")
                or id(item)
            )
            if item_key in seen:
                continue
            seen.add(item_key)
            items.append(item)

    for container_key in ("extendedEntities", "extended_entities"):
        container = tweet.get(container_key)
        if not isinstance(container, dict):
            continue
        media = container.get("media")
        if not isinstance(media, list):
            continue
        for item in media:
            if not isinstance(item, dict):
                continue
            item_key = str(item.get("media_key") or item.get("id_str") or id(item))
            if item_key in seen:
                continue
            seen.add(item_key)
            items.append(item)
    return items


def resolution_area(url: str) -> int:
    match = RESOLUTION_RE.search(url)
    if not match:
        return 0
    width, height = (int(match.group(1)), int(match.group(2)))
    return width * height


def normalized_bitrate(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def direct_mp4_variant(media: dict[str, Any]) -> dict[str, Any] | None:
    media_type = str(media.get("type") or "").lower()
    if media_type not in {"animated_gif", "video"}:
        return None

    url = media.get("mediaUrl") or media.get("url")
    if not isinstance(url, str):
        return None

    parsed = urllib.parse.urlparse(url)
    if not parsed.path.lower().endswith(".mp4"):
        return None

    return {
        "content_type": "video/mp4",
        "url": url,
        "bitrate": media.get("bitrate"),
    }


def best_mp4_variant(media: dict[str, Any]) -> dict[str, Any] | None:
    direct_variant = direct_mp4_variant(media)
    if direct_variant is not None:
        return direct_variant

    video_info = media.get("video_info")
    if not isinstance(video_info, dict):
        return None
    variants = video_info.get("variants")
    if not isinstance(variants, list):
        return None

    mp4_variants = [
        variant
        for variant in variants
        if isinstance(variant, dict)
        and variant.get("content_type") == "video/mp4"
        and isinstance(variant.get("url"), str)
    ]
    if not mp4_variants:
        return None

    return max(
        mp4_variants,
        key=lambda variant: (
            normalized_bitrate(variant.get("bitrate")),
            resolution_area(variant["url"]),
        ),
    )


def downloadable_videos(tweet: dict[str, Any]) -> list[dict[str, Any]]:
    videos: list[dict[str, Any]] = []
    for index, media in enumerate(media_items(tweet), start=1):
        variant = best_mp4_variant(media)
        if variant is None:
            continue
        videos.append(
            {
                "media_index": index,
                "media_key": media.get("media_key") or media.get("id_str"),
                "type": media.get("type"),
                "content_type": variant["content_type"],
                "bitrate": normalized_bitrate(variant.get("bitrate")) or None,
                "url": variant["url"],
            }
        )
    return videos


def validate_download_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_MEDIA_HOSTS:
        raise ValueError("Media downloads are limited to https://video.twimg.com.")
    if parsed.username or parsed.password:
        raise ValueError("Media download URLs must not include credentials.")


def output_path(
    *,
    output_dir: Path,
    tweet_id: str,
    video: dict[str, Any],
    filename: str | None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    if filename:
        path = Path(filename)
        if path.name != filename:
            raise ValueError("--filename must be a plain filename, not a path.")
        if path.suffix.lower() != ".mp4":
            path = path.with_suffix(".mp4")
        return output_dir / path

    bitrate = video.get("bitrate")
    bitrate_part = f"-{bitrate}" if bitrate else ""
    return output_dir / f"{tweet_id}-media-{video['media_index']}{bitrate_part}.mp4"


def download_file(url: str, target: Path, *, overwrite: bool = False) -> int:
    validate_download_url(url)
    if target.exists() and not overwrite:
        raise FileExistsError(f"{target} already exists. Pass --overwrite to replace it.")

    tmp_target = target.with_name(f".{target.name}.part")
    if tmp_target.exists():
        tmp_target.unlink()

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    ssl_context = build_ssl_context()

    try:
        with urllib.request.urlopen(
            request,
            timeout=60,
            context=ssl_context,
        ) as response, tmp_target.open("wb") as handle:
            while True:
                chunk = response.read(BUFFER_SIZE)
                if not chunk:
                    break
                handle.write(chunk)
        bytes_written = tmp_target.stat().st_size
        tmp_target.replace(target)
        return bytes_written
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} while downloading media") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while downloading media: {exc}") from exc
    finally:
        if tmp_target.exists():
            tmp_target.unlink()


def download_tweet_media(
    *,
    tweet_input: str,
    output_dir: Path,
    filename: str | None,
    first_only: bool,
    overwrite: bool,
    api_key: str | None,
    api_provider: str | None = None,
) -> dict[str, Any]:
    tweet_id = extract_tweet_id(tweet_input)
    provider = normalize_api_provider(api_provider)
    key = get_api_key(api_key, provider)
    tweet = fetch_tweet(tweet_id, key, provider)
    videos = downloadable_videos(tweet)
    if first_only:
        videos = videos[:1]
    if not videos:
        raise RuntimeError("No downloadable MP4 video variants found for this tweet.")
    if filename and len(videos) != 1:
        raise ValueError("--filename can only be used when one video file is selected.")

    files: list[dict[str, Any]] = []
    for video in videos:
        target = output_path(
            output_dir=output_dir,
            tweet_id=tweet_id,
            video=video,
            filename=filename,
        )
        bytes_written = download_file(video["url"], target, overwrite=overwrite)
        files.append(
            {
                "path": str(target.resolve()),
                "bytes": bytes_written,
                **video,
            }
        )

    return {
        "kind": "media_download",
        "tweet_id": tweet_id,
        "files": files,
        "source": provider_source_name(provider),
    }


def main() -> int:
    args = parse_args()
    try:
        result = download_tweet_media(
            tweet_input=requested_input(args),
            output_dir=Path(args.output_dir),
            filename=args.filename,
            first_only=args.first,
            overwrite=args.overwrite,
            api_key=args.api_key,
            api_provider=args.api_provider,
        )
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"twitterapi-x-reader error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
