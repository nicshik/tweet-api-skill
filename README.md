# TwitterAPI X Reader

Portable skill and helper scripts for working with X (Twitter) through `twitterapi.io`.

## Overview

This repository packages a reusable skill plus terminal helpers for reading tweets, X Articles, and other documented `twitterapi.io` endpoints without relying on direct `x.com` rendering.

It is designed for people who want:

- a portable skill install in `~/.codex/skills/twitterapi_x_reader`;
- simple terminal commands like `xread` and `xapi`;
- a stable path for research, summarization, and structured extraction from X.

## What Is Included

- `SKILL.md` for agent environments that support skill-style workflows
- `agents/openai.yaml` for UI metadata
- `references/` with quickstart, human-readable notes, and research examples
- `scripts/` with Python helpers
- `bin/xread` and `bin/xapi` terminal wrappers
- `install_portable.sh` for install and update

## Installation

From the repository root:

```bash
chmod +x ./install_portable.sh
./install_portable.sh
```

Then create your local key file if it does not already exist:

```bash
mkdir -p ~/.codex/skills/twitterapi_x_reader
printf '%s\n' 'TWITTERAPI_IO_KEY=your_key_here' > ~/.codex/skills/twitterapi_x_reader/.env.local
```

If your shell does not already include `~/.local/bin` in `PATH`, add it.

## Quick Start

Fetch a tweet or article:

```bash
xread "https://x.com/ZenithTON/status/2046570503801119055"
```

Force article mode:

```bash
xread "2046570503801119055" --mode article
```

Call any documented endpoint:

```bash
xapi --method GET --path /oapi/my/info --query-json '{}'
```

## Practical Workflows

Read a tweet or X Article and then analyze it:

```bash
xread "https://x.com/ZenithTON/status/2046570503801119055"
```

Look up the author profile:

```bash
xapi --method GET --path /twitter/user/info --query-json '{"userName":"ZenithTON"}'
```

Pull the author's recent tweets:

```bash
xapi --method GET --path /twitter/user/last_tweets --query-json '{"userName":"ZenithTON","includeReplies":false}'
```

Inspect replies:

```bash
xapi --method GET --path /twitter/tweet/replies/v2 --query-json '{"tweetId":"2046570503801119055","queryType":"Latest"}'
```

Inspect quote tweets:

```bash
xapi --method GET --path /twitter/tweet/quotes --query-json '{"tweetId":"2046570503801119055","includeReplies":false}'
```

Search accounts by topic:

```bash
xapi --method GET --path /twitter/user/search --query-json '{"query":"TON AI"}'
```

Search tweets by topic:

```bash
xapi --method GET --path /twitter/tweet/advanced_search --query-json '{"query":"\"AI agents\" Telegram TON","queryType":"Top"}'
```

For more detailed examples, see:

- `references/research_examples.md`
- `references/что_умеет_инструмент.md`
- `references/api_quickstart.md`
- `references/endpoint_catalog.md`

## API Key Handling

This repository does not store API keys.

The expected local key file is:

```text
~/.codex/skills/twitterapi_x_reader/.env.local
```

Example:

```text
TWITTERAPI_IO_KEY=your_key_here
```

## Update Flow

After pulling new changes from this repository, refresh the portable install with:

```bash
./install_portable.sh
```

This updates the installed skill and global wrappers while preserving the local `.env.local` file.

## Notes

- The default posture is read-only.
- Mutating API endpoints should only be used intentionally.
- `certifi` is supported when available, but the scripts can also fall back to the system certificate store.

## License

MIT
