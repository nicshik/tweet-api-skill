#!/usr/bin/env python3
"""Generic documented endpoint caller for twitterapi.io."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from twitterapi_client import get_api_key, request_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call any documented twitterapi.io endpoint."
    )
    parser.add_argument("--method", default="GET", help="HTTP method, e.g. GET or POST.")
    parser.add_argument(
        "--path",
        required=True,
        help="Official API path like /twitter/tweets or full https:// URL.",
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
        "--api-key",
        help="Optional override. Prefer TWITTERAPI_IO_KEY env var.",
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

        api_key = get_api_key(args.api_key)
        result = request_json(
            method=args.method,
            path=args.path,
            api_key=api_key,
            query=query,
            body=body,
        )
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"twitterapi_x_reader error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
