# Endpoint Catalog

This file tracks the official capability groups exposed in the `twitterapi.io` docs so the skill remains broader than just tweet and article reads.

Primary references:

- `https://docs.twitterapi.io/introduction`
- `https://docs.twitterapi.io/api-reference/introduction`

## Official Groups To Support

Based on the official docs navigation, this skill should remain ready to call endpoints across these groups:

### Core auth and account

- Authentication
- My account info
- My bookmarks
- My followed lists

### User endpoints

- User by user name
- User by id
- User search
- User tweets
- User replies
- Following
- Followers
- Affiliates
- Highlights
- Articles by user
- Subscriptions

### Tweet endpoints

- Tweet by ids
- Tweet details by id
- Tweet by media id
- Article
- Quotes
- Retweets
- Replies
- Tweet likers
- Tweet search
- Advanced search
- Batch search

### Lists, communities, spaces, trends

- List endpoints
- Community endpoints
- Space endpoints
- Trends

### Write and action endpoints

- Post Tweet
- Reply
- Tweet from media
- Like / unlike
- Retweet / unretweet
- Bookmark / delete bookmark
- Follow / unfollow
- Community reply actions

### Webhooks, websocket rules, and stream

- Webhook creation and management
- Websocket filter rule management
- Stream consumption

## Usage Strategy

- For common research reads, use `twitterapi_fetch.py` or `twitterapi_call.py`.
- For any endpoint not already wrapped by a specialized helper, use `twitterapi_call.py` with the exact official path and request shape from the docs.
- For mutating actions, require explicit user intent and prefer the exact documented payload from the corresponding endpoint page.

## Deliberate Non-Goals

- This reference does not freeze every path or request schema inside the skill body.
- The docs are the source of truth for endpoint-specific query names and bodies.
- The local generic caller exists so we can use newly added endpoints without rewriting the skill every time.
