# TwitterAPI X Reader

Portable skill and helper scripts for working with X (Twitter) via `twitterapi.io`.

## What is inside

This repository contains:

- a reusable skill package for Codex and similar agent environments;
- helper Python scripts for reading tweets, X Articles, and any documented `twitterapi.io` endpoint;
- portable terminal commands `xread` and `xapi`;
- an install/update script that syncs the skill into `~/.codex/skills/twitterapi_x_reader` and installs the global commands into `~/.local/bin`.

## Install

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

## Usage

Fetch a tweet or article:

```bash
xread "https://x.com/ZenithTON/status/2046570503801119055"
```

Call any documented endpoint:

```bash
xapi --method GET --path /oapi/my/info --query-json '{}'
```

## Structure

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`
- `bin/`
- `install_portable.sh`

## Notes

- The API key is not stored in the repository.
- The expected local key file is `~/.codex/skills/twitterapi_x_reader/.env.local`.
- Mutating API actions should only be used when explicitly intended.
