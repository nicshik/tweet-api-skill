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
- `references/` with quickstart and endpoint notes
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
