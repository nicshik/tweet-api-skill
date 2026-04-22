#!/usr/bin/env python3
"""Shared helpers for twitterapi.io skill scripts."""

from __future__ import annotations

import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

try:
    import certifi
except ImportError:  # pragma: no cover
    certifi = None


API_BASE = "https://api.twitterapi.io"
TWEET_RE = re.compile(r"(?:x|twitter)\.com/[^/]+/status/(\d+)")
ID_RE = re.compile(r"^\d+$")


def extract_tweet_id(value: str) -> str:
    value = value.strip()
    if ID_RE.fullmatch(value):
        return value

    match = TWEET_RE.search(value)
    if match:
        return match.group(1)

    raise ValueError(
        "Could not extract tweet id. Pass a full tweet URL like "
        "https://x.com/user/status/<id> or a raw numeric id."
    )


def get_api_key(cli_key: str | None) -> str:
    api_key = cli_key or os.getenv("TWITTERAPI_IO_KEY") or os.getenv("X_API_KEY")
    if api_key:
        return api_key

    local_env = Path(__file__).resolve().parent.parent / ".env.local"
    if local_env.exists():
        for line in local_env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "TWITTERAPI_IO_KEY" and value.strip():
                return value.strip()

    raise RuntimeError(
        "Missing API key. Set TWITTERAPI_IO_KEY in the environment, "
        "create .env.local next to the installed skill, or pass --api-key."
    )


def _build_url(path: str, query: dict[str, Any] | None = None) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        base = path
    else:
        normalized_path = path if path.startswith("/") else f"/{path}"
        base = f"{API_BASE}{normalized_path}"

    if not query:
        return base

    normalized_query: dict[str, str] = {}
    for key, value in query.items():
        if value is None:
            continue
        if isinstance(value, bool):
            normalized_query[key] = "true" if value else "false"
        else:
            normalized_query[key] = str(value)

    if not normalized_query:
        return base

    return f"{base}?{urllib.parse.urlencode(normalized_query)}"


def _build_ssl_context() -> ssl.SSLContext:
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


def request_json(
    *,
    method: str,
    path: str,
    api_key: str,
    query: dict[str, Any] | None = None,
    body: dict[str, Any] | list[Any] | None = None,
) -> dict[str, Any]:
    url = _build_url(path, query)
    data = None
    headers = {
        "X-API-Key": api_key,
        "Accept": "application/json",
        "User-Agent": "tweet-api-skill/0.3",
    }

    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=data,
        method=method.upper(),
        headers=headers,
    )
    ssl_context = _build_ssl_context()

    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {"status": "success"}
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from twitterapi.io: {body_text}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while calling twitterapi.io: {exc}") from exc
