#!/bin/zsh
set -euo pipefail

REPO_ROOT=${0:A:h}
TARGET_SKILL_DIR="$HOME/.codex/skills/twitterapi-x-reader"
LEGACY_SKILL_DIR="$HOME/.codex/skills/twitterapi_x_reader"
TARGET_BIN_DIR="$HOME/.local/bin"

mkdir -p "$TARGET_SKILL_DIR"
mkdir -p "$TARGET_BIN_DIR"

if [[ ! -f "$TARGET_SKILL_DIR/.env.local" && -f "$LEGACY_SKILL_DIR/.env.local" ]]; then
  cp "$LEGACY_SKILL_DIR/.env.local" "$TARGET_SKILL_DIR/.env.local"
fi

# Sync the skill while preserving the local API key file if it already exists.
rsync -a --delete \
  --exclude '.git' \
  --exclude '.github' \
  --exclude '.gitignore' \
  --exclude '.env.example' \
  --exclude 'README.md' \
  --exclude 'CONTRIBUTING.md' \
  --exclude 'SECURITY.md' \
  --exclude 'install_portable.sh' \
  --exclude 'bin' \
  --exclude 'tests' \
  --exclude '*.egg-info' \
  --exclude 'build' \
  --exclude 'dist' \
  --exclude '__pycache__' \
  --exclude '.env.local' \
  "$REPO_ROOT/" "$TARGET_SKILL_DIR/"

install -m 755 "$REPO_ROOT/bin/xread" "$TARGET_BIN_DIR/xread"
install -m 755 "$REPO_ROOT/bin/xapi" "$TARGET_BIN_DIR/xapi"
install -m 755 "$REPO_ROOT/bin/xmedia" "$TARGET_BIN_DIR/xmedia"

echo "Portable TwitterAPI X Reader updated."
echo "Skill: $TARGET_SKILL_DIR"
echo "Commands: $TARGET_BIN_DIR/xread, $TARGET_BIN_DIR/xapi, $TARGET_BIN_DIR/xmedia"

echo "If the commands are not found in a new terminal session, ensure ~/.local/bin is on PATH."

if [[ -f "$TARGET_SKILL_DIR/.env.local" ]]; then
  echo "API key file preserved: $TARGET_SKILL_DIR/.env.local"
else
  echo "No API key file found. Create: $TARGET_SKILL_DIR/.env.local"
  echo 'Example: TWITTERAPI_IO_KEY=your_key_here'
fi

if [[ -d "$LEGACY_SKILL_DIR" ]]; then
  echo "Legacy install detected: $LEGACY_SKILL_DIR"
  echo "The new skill name is twitterapi-x-reader; legacy xread/xapi/xmedia lookup remains supported."
fi
