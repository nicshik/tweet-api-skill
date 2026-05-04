# twitterapi.io Quickstart

Official docs used for this skill:

- Introduction: `https://docs.twitterapi.io/introduction`
- API Reference intro: `https://docs.twitterapi.io/api-reference/introduction`
- Authentication: `https://docs.twitterapi.io/authentication`
- Get Tweets by IDs: `https://docs.twitterapi.io/api-reference/endpoint/get_tweet_by_ids`
- Get Article: `https://docs.twitterapi.io/api-reference/endpoint/get_article`

## Auth

Every request requires header:

```text
X-API-Key: <api-key>
```

This skill expects the key in:

```text
TWITTERAPI_IO_KEY
```

Fallback for a personal local install:

```text
~/.codex/skills/twitterapi-x-reader/.env.local
```

## Operational Model

- `twitterapi_fetch.py` is a narrow helper for the common `tweet` and `article` paths.
- `twitterapi_call.py` is the generic helper for any documented endpoint, any supported method, and any query/body shape from the official docs.
- The docs remain the source of truth for endpoint-specific payloads.

## Examples

### Tweet details

```text
GET /twitter/tweets?tweet_ids=<id>
```

### X Article by parent tweet id

```text
GET /twitter/article?tweet_id=<id>
```

### Generic documented call

```text
python3 scripts/twitterapi_call.py --method GET --path /twitter/tweets --query-json '{"tweet_ids":"123"}'
```

## Notes

- Article endpoint expects the tweet id of the article post, not the `x.com/i/article/...` id.
- Direct X rendering can fail because of auth, JS, regional rendering, or bot protection; this skill exists to bypass that fragility.
- Mutating endpoints should only be used when the user explicitly requests an action.
