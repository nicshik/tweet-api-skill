#!/usr/bin/env python3
"""Shared helpers for X/Twitter API skill scripts."""

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


TWITTERAPI_IO_PROVIDER = "twitterapi_io"
XQUIK_PROVIDER = "xquik"
DEFAULT_PROVIDER = TWITTERAPI_IO_PROVIDER
API_BASES = {
    TWITTERAPI_IO_PROVIDER: "https://api.twitterapi.io",
    XQUIK_PROVIDER: "https://xquik.com/api/v1",
}
API_HOSTS = {
    provider: urllib.parse.urlparse(api_base).netloc
    for provider, api_base in API_BASES.items()
}
API_PROVIDER_ALIASES = {
    "twitterapi": TWITTERAPI_IO_PROVIDER,
    "twitterapi.io": TWITTERAPI_IO_PROVIDER,
    "twitterapi_io": TWITTERAPI_IO_PROVIDER,
    "xquik": XQUIK_PROVIDER,
    "xquik.com": XQUIK_PROVIDER,
}
PROVIDER_ENV_KEYS = ("X_API_PROVIDER", "API_PROVIDER")
API_KEY_SOURCES = {
    TWITTERAPI_IO_PROVIDER: ("TWITTERAPI_IO_KEY", "X_API_KEY"),
    XQUIK_PROVIDER: ("XQUIK_API_KEY", "X_API_KEY"),
}
XQUIK_API_CONTRACT = "2026-04-29"
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


def _local_env_items() -> list[tuple[str, str]]:
    local_env = Path(__file__).resolve().parent.parent / ".env.local"
    if not local_env.exists():
        return []

    items: list[tuple[str, str]] = []
    for line in local_env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        items.append((key.strip(), value))
    return items


def normalize_api_provider(api_provider: str | None = None) -> str:
    raw_provider = api_provider
    if raw_provider is None:
        for env_key in PROVIDER_ENV_KEYS:
            env_value = os.getenv(env_key)
            if env_value:
                raw_provider = env_value
                break
        if raw_provider is None:
            for key, value in _local_env_items():
                if key in PROVIDER_ENV_KEYS:
                    raw_provider = value
                    break

    if raw_provider is None or not raw_provider.strip():
        return DEFAULT_PROVIDER

    normalized = raw_provider.strip().lower().replace("-", "_")
    provider = API_PROVIDER_ALIASES.get(normalized)
    if provider:
        return provider

    allowed = ", ".join(sorted({*API_PROVIDER_ALIASES, *API_BASES}))
    raise ValueError(f"Unsupported API provider: {raw_provider}. Allowed: {allowed}.")


def provider_source_name(api_provider: str | None = None) -> str:
    provider = normalize_api_provider(api_provider)
    if provider == XQUIK_PROVIDER:
        return "xquik"
    return "twitterapi.io"


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
            f"{source} contains a placeholder API key. Set a real provider API key."
        )

    return value


def get_api_key(cli_key: str | None, api_provider: str | None = None) -> str:
    provider = normalize_api_provider(api_provider)
    key_sources = API_KEY_SOURCES[provider]
    for source, raw_value in [("--api-key", cli_key)] + [
        (env_key, os.getenv(env_key)) for env_key in key_sources
    ]:
        api_key = _clean_api_key(raw_value, source)
        if api_key:
            return api_key

    for key, value in _local_env_items():
        if key in key_sources:
            api_key = _clean_api_key(value, ".env.local")
            if api_key:
                return api_key

    primary_key = key_sources[0]
    raise RuntimeError(
        f"Missing API key. Set {primary_key} in the environment, create "
        ".env.local next to the installed skill, or pass --api-key."
    )


def _validated_base_url(path: str, api_provider: str | None = None) -> str:
    provider = normalize_api_provider(api_provider)
    api_base = API_BASES[provider]
    api_host = API_HOSTS[provider]
    parsed_base = urllib.parse.urlparse(api_base)
    if path.startswith("http://") or path.startswith("https://"):
        parsed = urllib.parse.urlparse(path)
        if parsed.scheme != "https" or parsed.netloc != api_host:
            raise ValueError(
                f"Full URLs must use {api_base}. Prefer passing an official path."
            )
        if parsed.username or parsed.password:
            raise ValueError("Full API URLs must not include credentials.")
        if parsed_base.path and not (
            parsed.path == parsed_base.path
            or parsed.path.startswith(f"{parsed_base.path}/")
        ):
            raise ValueError(
                f"Full URLs for {provider_source_name(provider)} must stay under "
                f"{api_base}."
            )
        return path

    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{api_base}{normalized_path}"


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


def _build_url(
    path: str,
    query: dict[str, Any] | None = None,
    api_provider: str | None = None,
) -> str:
    base = _validated_base_url(path, api_provider)
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
    api_provider: str | None = None,
) -> dict[str, Any]:
    provider = normalize_api_provider(api_provider)
    method = method.upper()
    if method not in ALLOWED_METHODS:
        raise ValueError(
            f"Unsupported HTTP method: {method}. "
            f"Allowed methods: {', '.join(sorted(ALLOWED_METHODS))}."
        )

    url = _build_url(path, query, provider)
    data = None
    headers = {
        "Accept": "application/json",
        "User-Agent": "tweet-api-skill/0.4.3",
    }
    if provider == XQUIK_PROVIDER:
        headers["x-api-key"] = api_key
        headers["xquik-api-contract"] = XQUIK_API_CONTRACT
    else:
        headers["X-API-Key"] = api_key

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
        source = provider_source_name(provider)
        raise RuntimeError(f"HTTP {exc.code} from {source}: {body_text}") from exc
    except urllib.error.URLError as exc:
        source = provider_source_name(provider)
        raise RuntimeError(f"Network error while calling {source}: {exc}") from exc
