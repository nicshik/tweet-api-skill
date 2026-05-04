# TwitterAPI X Reader

[![CI](https://github.com/nicshik/tweet-api-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/nicshik/tweet-api-skill/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Portable skill and helper scripts for working with X (Twitter) through `twitterapi.io`.

[🇷🇺 Читать на русском](README.ru.md)

## Overview

This repository packages a reusable skill plus terminal helpers for reading tweets, X Articles, and other documented `twitterapi.io` endpoints without relying on direct `x.com` rendering.

It is designed for people who want:

- a portable skill install in `~/.codex/skills/twitterapi-x-reader`;
- simple terminal commands like `xread` and `xapi`;
- a stable path for research, summarization, and structured extraction from X.

This project is not affiliated with X Corp., Twitter, or `twitterapi.io`.

Maintainer: [`nicshik`](https://github.com/nicshik).

## What Is Included

- `SKILL.md` for agent environments that support skill-style workflows
- `agents/openai.yaml` for UI metadata
- `references/` with quickstart, human-readable notes, and research examples
- `scripts/` with Python helpers
- `bin/xread` and `bin/xapi` terminal wrappers
- `install_portable.sh` for install and update

## Requirements

- Python 3.10 or newer
- `zsh`, `rsync`, and `install` for `install_portable.sh`
- a `twitterapi.io` API key

## Installation

### Portable Skill Install

From the repository root:

```bash
chmod +x ./install_portable.sh
./install_portable.sh
```

Then create your local key file if it does not already exist:

```bash
mkdir -p ~/.codex/skills/twitterapi-x-reader
printf '%s\n' 'TWITTERAPI_IO_KEY=your_key_here' > ~/.codex/skills/twitterapi-x-reader/.env.local
```

If your shell does not already include `~/.local/bin` in `PATH`, add it.

### CLI Package Install

If you only need the `xread` and `xapi` console scripts, install the package directly:

```bash
python -m pip install "git+https://github.com/nicshik/tweet-api-skill.git"
```

The package install does not install the Codex skill files. Use `TWITTERAPI_IO_KEY` or `--api-key` for authentication.

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

`xapi` accepts official API paths by default. Full URLs are only accepted for `https://api.twitterapi.io` so the API key is not sent to arbitrary hosts.

Mutating HTTP methods are blocked unless you pass `--allow-mutation`:

```bash
xapi --method POST --path /twitter/post/create --body-json '{"text":"draft"}' --allow-mutation
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
- `references/capabilities.md`
- `references/api_quickstart.md`
- `references/endpoint_catalog.md`

## API Key Handling

This repository does not store API keys.

The expected local key file is:

```text
~/.codex/skills/twitterapi-x-reader/.env.local
```

Example:

```text
TWITTERAPI_IO_KEY=your_key_here
```

The scripts also accept `--api-key`, but environment variables or `.env.local` are preferred because command-line arguments can be recorded in shell history.

## Development

Run the no-network tests:

```bash
python -m unittest discover -s tests
```

Check local documentation links:

```bash
python scripts/check_links.py
```

Verify the package entry points locally:

```bash
python -m pip install .
xapi --help
xread --help
```

Validate the skill metadata with the Skill Creator validator when available:

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
```

## Support / Security

Use GitHub Issues for questions, bugs, and feature requests.

Report security vulnerabilities privately through `SECURITY.md`. Do not open public issues with API keys, `.env.local`, private account data, or exploit details.

## Update Flow

After pulling new changes from this repository, refresh the portable install with:

```bash
./install_portable.sh
```

This updates the installed skill and global wrappers while preserving the local `.env.local` file.

Older local installs under `~/.codex/skills/twitterapi_x_reader` are detected during installation. The installer copies the legacy `.env.local` into the new hyphen-case skill directory when needed, and the `xread`/`xapi` wrappers still check the legacy path for compatibility.

## Notes

- The default posture is read-only.
- Mutating API endpoints should only be used intentionally.
- `certifi` is supported when available, but the scripts can also fall back to the system certificate store.
- See `SECURITY.md` before publishing logs, examples, or bug reports.

## License

MIT
