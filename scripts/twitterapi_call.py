#!/usr/bin/env python3
"""Generic documented endpoint caller for supported X/Twitter API providers."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from twitterapi_client import (
    TWITTERAPI_IO_PROVIDER,
    XQUIK_PROVIDER,
    get_api_key,
    normalize_api_provider,
    request_json,
)


MUTATING_METHODS = {"POST", "PATCH", "PUT", "DELETE"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call any documented endpoint on a supported provider."
    )
    parser.add_argument("--method", default="GET", help="HTTP method, e.g. GET or POST.")
    parser.add_argument(
        "--path",
        required=True,
        help=(
            "Official API path like /twitter/tweets or /x/tweets, or a full "
            "provider API URL."
        ),
    )
    parser.add_argument(
        "--query-json",
        default="{}",
        help="JSON object for query parameters.",
    )
    parser.add_argument(
        "--body-json",
        default="null",
        help="JSON object or array for request body.",
    )
    parser.add_argument(
        "--allow-mutation",
        action="store_true",
        help=(
            "Required for POST, PATCH, PUT, and DELETE endpoints. "
            "Use only after confirming the endpoint can mutate account state."
        ),
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


def parse_json_arg(raw: str, label: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid {label}: {exc}") from exc


def main() -> int:
    args = parse_args()
    try:
        query = parse_json_arg(args.query_json, "--query-json")
        body = parse_json_arg(args.body_json, "--body-json")

        if query is not None and not isinstance(query, dict):
            raise ValueError("--query-json must decode to a JSON object")
        if body is not None and not isinstance(body, (dict, list)):
            raise ValueError("--body-json must decode to null, object, or array")

        method = args.method.upper()
        if method in MUTATING_METHODS and not args.allow_mutation:
            raise ValueError(
                "POST, PATCH, PUT, and DELETE requests require --allow-mutation. "
                "Confirm the endpoint is intended to mutate account state before retrying."
            )

        api_provider = normalize_api_provider(args.api_provider)
        api_key = get_api_key(args.api_key, api_provider)
        result = request_json(
            method=method,
            path=args.path,
            api_key=api_key,
            query=query,
            body=body,
            api_provider=api_provider,
        )
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"twitterapi-x-reader error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
