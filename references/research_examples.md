# Research Workflow Examples

These examples use documented `twitterapi.io` endpoints and are intended for common research and analysis tasks.

Primary docs used:

- `GET /twitter/user/info`
- `GET /twitter/user/last_tweets`
- `GET /twitter/tweet/replies/v2`
- `GET /twitter/tweet/quotes`
- `GET /twitter/tweet/advanced_search`

## 1. Get article or tweet content quickly

```bash
xread "https://x.com/ZenithTON/status/2046570503801119055"
```

Or force article mode:

```bash
xread "2046570503801119055" --mode article
```

## 2. Get author profile by username

Official endpoint: `GET /twitter/user/info`

Query parameter from docs:

- `userName`

Example:

```bash
xapi --method GET --path /twitter/user/info --query-json '{"userName":"ZenithTON"}'
```

## 3. Get the latest tweets from a user

Official endpoint: `GET /twitter/user/last_tweets`

Query parameters from docs:

- `userId` or `userName`
- `cursor`
- `includeReplies`

Example:

```bash
xapi --method GET --path /twitter/user/last_tweets --query-json '{"userName":"ZenithTON","includeReplies":false}'
```

## 4. Get replies to a tweet

Official endpoint: `GET /twitter/tweet/replies/v2`

Query parameters from docs:

- `tweetId`
- `cursor`
- `queryType` with values `Relevance`, `Latest`, `Likes`

Example:

```bash
xapi --method GET --path /twitter/tweet/replies/v2 --query-json '{"tweetId":"2046570503801119055","queryType":"Latest"}'
```

## 5. Get quote tweets for a tweet

Official endpoint: `GET /twitter/tweet/quotes`

Query parameters from docs:

- `tweetId`
- `sinceTime`
- `untilTime`
- `includeReplies`
- `cursor`

Example:

```bash
xapi --method GET --path /twitter/tweet/quotes --query-json '{"tweetId":"2046570503801119055","includeReplies":false}'
```

## 6. Search users by keyword

Official endpoint: `GET /twitter/user/search`

Query parameters from docs:

- `query`
- `cursor`

Example:

```bash
xapi --method GET --path /twitter/user/search --query-json '{"query":"TON AI"}'
```

## 7. Search tweets by topic

Official endpoint: `GET /twitter/tweet/advanced_search`

Query parameters from docs:

- `query`
- `queryType` with values `Latest` or `Top`
- `cursor`

Example:

```bash
xapi --method GET --path /twitter/tweet/advanced_search --query-json '{"query":"\"AI agents\" Telegram TON","queryType":"Top"}'
```

## Notes

- For tweet or article reading, prefer `xread`.
- For all other workflows, prefer `xapi`.
- Use pagination with `cursor` when the API returns `has_next_page: true`.
- Some search and timeline endpoints can consume credits quickly; use them intentionally.
