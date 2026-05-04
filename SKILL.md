---
name: twitterapi-x-reader
description: Portable workflow for using twitterapi.io official endpoints for X or Twitter reads, articles, search, user data, communities, lists, spaces, trends, streams, webhook rules, and explicitly requested write actions.
license: MIT
metadata:
  category: research
  capability_taxonomy_ids:
    - cap.research.social_media_fetch
    - cap.research.twitter_article_parse
  distribution_scope: public
  invocation_strategy: explicit
  version: v0.4.1
  source_of_truth: github:nicshik/tweet-api-skill
---

# TwitterAPI X Reader

Use this skill when you need reliable access to X or Twitter data through `twitterapi.io`, especially:

- tweet details by URL or id;
- long-form X Articles linked from a tweet;
- user lookup and user search;
- followers, following, replies, retweets, quotes, likers, and bookmarks;
- communities, lists, spaces, and trends;
- account-level endpoints such as bookmarks and followed lists;
- webhook rules, websocket rules, or stream endpoints;
- explicitly requested write actions like posting, liking, retweeting, bookmarking, following, or community replies;
- structured JSON for later analysis, summarization, or automation.

This skill is intentionally explicit-only because `twitterapi.io` consumes paid credits and also exposes mutating endpoints.

## Preconditions

- Preferred: `TWITTERAPI_IO_KEY` is present in the environment.
- Supported fallback: a local `.env.local` file next to the installed skill, containing `TWITTERAPI_IO_KEY=...`.
- If neither source exists, the skill must stop and ask for local configuration rather than requesting the secret in output.

## Default Flow

1. Decide whether the task is:
   - a common content read (`tweet` or `article`);
   - another documented read endpoint;
   - a mutating account action.
2. For tweets and articles, run `scripts/twitterapi_fetch.py`.
3. For any other documented endpoint, run `scripts/twitterapi_call.py` with the official method, path, and query/body payload.
4. Inspect the JSON and summarize or transform it for the user.
5. Mention when the result came from `twitterapi.io` rather than direct X rendering.

## Coverage

This skill should be treated as covering the official `twitterapi.io` surface documented in:

- `Introduction`
- `API Reference`
- `Authentication`

At minimum, the workflow must remain ready for these method groups:

- tweet reads and search;
- article fetches;
- user reads and graph reads;
- list, community, space, and trend reads;
- account endpoints under `my`;
- post and action endpoints under v2;
- community action endpoints;
- webhook and websocket rule management;
- stream endpoints.

## Input Rules

- Preferred input for tweet-centric work: full tweet URL like `https://x.com/user/status/123`.
- Also allowed: raw tweet id.
- Do not treat `x.com/i/article/<id>` as sufficient input by itself; the API article endpoint expects the parent tweet id.
- For generic endpoint usage, prefer exact official paths from the docs.
- If a full URL is used instead of a path, it must stay under `https://api.twitterapi.io`; do not send the API key to arbitrary hosts.

## Command Patterns

- Auto-detect article vs tweet:
  - `python3 scripts/twitterapi_fetch.py --input "<url-or-id>"`
- Force article lookup:
  - `python3 scripts/twitterapi_fetch.py --input "<url-or-id>" --mode article`
- Force tweet lookup:
  - `python3 scripts/twitterapi_fetch.py --input "<url-or-id>" --mode tweet`
- Generic documented GET endpoint:
  - `python3 scripts/twitterapi_call.py --method GET --path "<official-path>" --query-json '{"key":"value"}'`
- Generic documented POST endpoint:
  - `python3 scripts/twitterapi_call.py --method POST --path "<official-path>" --body-json '{"key":"value"}' --allow-mutation`
- Generic documented PATCH or DELETE endpoint:
  - `python3 scripts/twitterapi_call.py --method PATCH --path "<official-path>" --body-json '{...}' --allow-mutation`
  - `python3 scripts/twitterapi_call.py --method DELETE --path "<official-path>" --query-json '{...}' --allow-mutation`

## Endpoint Selection Rules

- Prefer `twitterapi_fetch.py` for article-or-tweet workflows because it normalizes the result.
- Prefer `twitterapi_call.py` for every other official endpoint.
- Use raw official paths from the docs if no local shorthand exists.
- Keep the skill aligned with the docs instead of inventing unofficial endpoint names.

## Safety And Cost Rules

- Default to read-only methods unless the user explicitly asks for an action.
- `POST`, `PATCH`, `PUT`, and `DELETE` require `--allow-mutation`; use it only after confirming the exact intended account or community action.
- Prefer `--mode auto` only when article presence is plausible and useful.
- Remember that article fetches and search endpoints may cost more than simple reads.
- Never print the API key.
- Prefer environment variables over CLI flags for the key to avoid shell history leakage.
- If a write endpoint fails, surface the API error cleanly and do not retry blindly.

## References

- `references/capabilities.md`
- `references/api_quickstart.md`
- `references/endpoint_catalog.md`
