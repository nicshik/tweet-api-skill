#!/usr/bin/env python3
"""Fetch tweet or X Article data from twitterapi.io."""

from __future__ import annotations

import argparse
import json
import sys

from twitterapi_client import extract_tweet_id, get_api_key, request_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch X tweet details or X Article data via twitterapi.io."
    )
    parser.add_argument("--input", required=True, help="Tweet URL or raw tweet id.")
    parser.add_argument(
        "--mode",
        choices=("auto", "article", "tweet"),
        default="auto",
        help="Lookup mode. Default: auto.",
    )
    parser.add_argument(
        "--api-key",
        help="Optional override. Prefer TWITTERAPI_IO_KEY env var.",
    )
    return parser.parse_args()


def fetch_article(tweet_id: str, api_key: str) -> dict:
    payload = request_json(
        method="GET",
        path="/twitter/article",
        query={"tweet_id": tweet_id},
        api_key=api_key,
    )
    article = payload.get("article")
    if payload.get("status") == "success" and article:
        return {
            "kind": "article",
            "tweet_id": tweet_id,
            "article": article,
            "source": "twitterapi.io",
        }
    raise RuntimeError(payload.get("message") or "Article not found")


def fetch_tweet(tweet_id: str, api_key: str) -> dict:
    payload = request_json(
        method="GET",
        path="/twitter/tweets",
        query={"tweet_ids": tweet_id},
        api_key=api_key,
    )
    tweets = payload.get("tweets") or []
    if payload.get("status") == "success" and tweets:
        return {
            "kind": "tweet",
            "tweet_id": tweet_id,
            "tweet": tweets[0],
            "source": "twitterapi.io",
        }
    raise RuntimeError(payload.get("message") or "Tweet not found")


def main() -> int:
    args = parse_args()
    try:
        tweet_id = extract_tweet_id(args.input)
        api_key = get_api_key(args.api_key)

        if args.mode == "article":
            result = fetch_article(tweet_id, api_key)
        elif args.mode == "tweet":
            result = fetch_tweet(tweet_id, api_key)
        else:
            try:
                result = fetch_article(tweet_id, api_key)
            except RuntimeError:
                result = fetch_tweet(tweet_id, api_key)

        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"twitterapi_x_reader error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
