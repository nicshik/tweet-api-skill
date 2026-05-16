#!/usr/bin/env python3
"""Fetch tweet or X Article data from a supported X/Twitter API provider."""

from __future__ import annotations

import argparse
import json
import sys

from twitterapi_client import (
    TWITTERAPI_IO_PROVIDER,
    XQUIK_PROVIDER,
    extract_tweet_id,
    get_api_key,
    normalize_api_provider,
    provider_source_name,
    request_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch X tweet details or X Article data via a supported provider."
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
        help="Optional override. Prefer TWITTERAPI_IO_KEY or XQUIK_API_KEY env var.",
    )
    parser.add_argument(
        "--api-provider",
        choices=(TWITTERAPI_IO_PROVIDER, XQUIK_PROVIDER),
        help="API provider. Defaults to X_API_PROVIDER, API_PROVIDER, or twitterapi_io.",
    )
    return parser.parse_args()


def fetch_article(
    tweet_id: str,
    api_key: str,
    api_provider: str = TWITTERAPI_IO_PROVIDER,
) -> dict:
    api_provider = normalize_api_provider(api_provider)
    if api_provider == XQUIK_PROVIDER:
        payload = request_json(
            method="GET",
            path=f"/x/articles/{tweet_id}",
            api_key=api_key,
            api_provider=api_provider,
        )
        article = payload.get("article")
        if article:
            return {
                "kind": "article",
                "tweet_id": tweet_id,
                "article": article,
                "source": provider_source_name(api_provider),
            }
        raise RuntimeError(payload.get("message") or "Article not found")

    payload = request_json(
        method="GET",
        path="/twitter/article",
        query={"tweet_id": tweet_id},
        api_key=api_key,
        api_provider=api_provider,
    )
    article = payload.get("article")
    if payload.get("status") == "success" and article:
        return {
            "kind": "article",
            "tweet_id": tweet_id,
            "article": article,
            "source": provider_source_name(api_provider),
        }
    raise RuntimeError(payload.get("message") or "Article not found")


def fetch_tweet(
    tweet_id: str,
    api_key: str,
    api_provider: str = TWITTERAPI_IO_PROVIDER,
) -> dict:
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
        if tweets:
            return {
                "kind": "tweet",
                "tweet_id": tweet_id,
                "tweet": tweets[0],
                "source": provider_source_name(api_provider),
            }
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
        return {
            "kind": "tweet",
            "tweet_id": tweet_id,
            "tweet": tweets[0],
            "source": provider_source_name(api_provider),
        }
    raise RuntimeError(payload.get("message") or "Tweet not found")


def main() -> int:
    args = parse_args()
    try:
        tweet_id = extract_tweet_id(args.input)
        api_provider = normalize_api_provider(args.api_provider)
        api_key = get_api_key(args.api_key, api_provider)

        if args.mode == "article":
            result = fetch_article(tweet_id, api_key, api_provider)
        elif args.mode == "tweet":
            result = fetch_tweet(tweet_id, api_key, api_provider)
        else:
            try:
                result = fetch_article(tweet_id, api_key, api_provider)
            except RuntimeError:
                result = fetch_tweet(tweet_id, api_key, api_provider)

        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"twitterapi-x-reader error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
