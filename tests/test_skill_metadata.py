import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FRONTMATTER_KEYS = {
    "allowed-tools",
    "description",
    "license",
    "metadata",
    "name",
}
REQUIRED_FRONTMATTER_KEYS = {"name", "description"}


def top_level_frontmatter_keys(text: str) -> set[str]:
    frontmatter = extract_frontmatter(text)
    keys: set[str] = set()
    for line in frontmatter.splitlines():
        if not line.strip() or line.startswith((" ", "-")):
            continue
        key, separator, _value = line.partition(":")
        if separator:
            keys.add(key)
    return keys


def extract_frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not match:
        raise AssertionError("SKILL.md is missing YAML frontmatter")
    return match.group(1)


def frontmatter_scalar(text: str, target_key: str) -> str:
    for line in extract_frontmatter(text).splitlines():
        if not line.strip() or line.startswith((" ", "-")):
            continue
        key, separator, _value = line.partition(":")
        if separator and key == target_key:
            return _value.strip()
    raise AssertionError(f"Missing frontmatter key: {target_key}")


class SkillMetadataTests(unittest.TestCase):
    def test_skill_frontmatter_uses_supported_keys(self) -> None:
        keys = top_level_frontmatter_keys(
            (ROOT / "SKILL.md").read_text(encoding="utf-8")
        )

        self.assertFalse(
            keys - ALLOWED_FRONTMATTER_KEYS,
            f"Unexpected SKILL.md frontmatter keys: {sorted(keys)}",
        )
        self.assertTrue(
            REQUIRED_FRONTMATTER_KEYS <= keys,
            f"Missing required SKILL.md keys: {sorted(REQUIRED_FRONTMATTER_KEYS - keys)}",
        )

    def test_skill_name_is_hyphen_case(self) -> None:
        name = frontmatter_scalar((ROOT / "SKILL.md").read_text(encoding="utf-8"), "name")

        self.assertRegex(name, r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


if __name__ == "__main__":
    unittest.main()
