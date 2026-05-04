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
API_HOST = urllib.parse.urlparse(API_BASE).netloc
ALLOWED_METHODS = {"GET", "POST", "PATCH", "PUT", "DELETE"}
PLACEHOLDER_API_KEYS = {
    "your_key_here",
    "<api-key>",
    "<api_key>",
    "replace_me",
    "changeme",
}
TWEET_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:mobile\.)?(?:x|twitter)\.com/"
    r"[^/?#]+/status(?:es)?/(\d+)"
)
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


def _clean_api_key(raw_value: str | None, source: str) -> str | None:
    if raw_value is None:
        return None

    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1].strip()

    if not value:
        return None

    if value.lower() in PLACEHOLDER_API_KEYS:
        raise RuntimeError(
            f"{source} contains a placeholder API key. Set a real TWITTERAPI_IO_KEY."
        )

    return value


def get_api_key(cli_key: str | None) -> str:
    for source, raw_value in (
        ("--api-key", cli_key),
        ("TWITTERAPI_IO_KEY", os.getenv("TWITTERAPI_IO_KEY")),
        ("X_API_KEY", os.getenv("X_API_KEY")),
    ):
        api_key = _clean_api_key(raw_value, source)
        if api_key:
            return api_key

    local_env = Path(__file__).resolve().parent.parent / ".env.local"
    if local_env.exists():
        for line in local_env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "TWITTERAPI_IO_KEY":
                api_key = _clean_api_key(value, ".env.local")
                if api_key:
                    return api_key

    raise RuntimeError(
        "Missing API key. Set TWITTERAPI_IO_KEY in the environment, "
        "create .env.local next to the installed skill, or pass --api-key."
    )


def _validated_base_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        parsed = urllib.parse.urlparse(path)
        if parsed.scheme != "https" or parsed.netloc != API_HOST:
            raise ValueError(
                "Full URLs must use https://api.twitterapi.io. "
                "Prefer passing an official path like /twitter/tweets."
            )
        if parsed.username or parsed.password:
            raise ValueError("Full API URLs must not include credentials.")
        return path

    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{API_BASE}{normalized_path}"


def _query_items(query: dict[str, Any] | None) -> list[tuple[str, str | list[str]]]:
    if not query:
        return []

    items: list[tuple[str, str | list[str]]] = []
    for key, value in query.items():
        if value is None:
            continue
        if isinstance(value, bool):
            items.append((key, "true" if value else "false"))
        elif isinstance(value, (list, tuple)):
            items.append((key, [str(item) for item in value]))
        else:
            items.append((key, str(value)))
    return items


def _build_url(path: str, query: dict[str, Any] | None = None) -> str:
    base = _validated_base_url(path)
    items = _query_items(query)
    if not items:
        return base

    parsed = urllib.parse.urlparse(base)
    existing_items = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query_string = urllib.parse.urlencode(existing_items + items, doseq=True)
    return urllib.parse.urlunparse(parsed._replace(query=query_string))


def build_ssl_context() -> ssl.SSLContext:
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
    method = method.upper()
    if method not in ALLOWED_METHODS:
        raise ValueError(
            f"Unsupported HTTP method: {method}. "
            f"Allowed methods: {', '.join(sorted(ALLOWED_METHODS))}."
        )

    url = _build_url(path, query)
    data = None
    headers = {
        "X-API-Key": api_key,
        "Accept": "application/json",
        "User-Agent": "tweet-api-skill/0.4.2",
    }

    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=headers,
    )
    ssl_context = build_ssl_context()

    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {"status": "success"}
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from twitterapi.io: {body_text}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while calling twitterapi.io: {exc}") from exc
