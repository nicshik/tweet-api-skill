# Contributing

## Local Checks

Run the no-network test suite before opening a pull request:

```bash
python -m unittest discover -s tests
```

Validate the skill metadata with the Skill Creator validator when it is available:

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
```

## Guidelines

- Keep `SKILL.md` concise and focused on agent instructions.
- Keep endpoint-specific examples in `references/`.
- Do not commit API keys or local `.env.local` files.
- Keep mutating API actions explicit-only.
