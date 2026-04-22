#!/bin/zsh
set -euo pipefail

REPO_ROOT=${0:A:h}
TARGET_SKILL_DIR="$HOME/.codex/skills/twitterapi_x_reader"
TARGET_BIN_DIR="$HOME/.local/bin"

mkdir -p "$TARGET_SKILL_DIR"
mkdir -p "$TARGET_BIN_DIR"

# Sync the skill while preserving the local API key file if it already exists.
rsync -a --delete \
  --exclude '.git' \
  --exclude '.gitignore' \
  --exclude 'README.md' \
  --exclude 'install_portable.sh' \
  --exclude 'bin' \
  --exclude '.env.local' \
  "$REPO_ROOT/" "$TARGET_SKILL_DIR/"

install -m 755 "$REPO_ROOT/bin/xread" "$TARGET_BIN_DIR/xread"
install -m 755 "$REPO_ROOT/bin/xapi" "$TARGET_BIN_DIR/xapi"

echo "Portable TwitterAPI X Reader updated."
echo "Skill: $TARGET_SKILL_DIR"
echo "Commands: $TARGET_BIN_DIR/xread, $TARGET_BIN_DIR/xapi"

echo "If the commands are not found in a new terminal session, ensure ~/.local/bin is on PATH."

if [[ -f "$TARGET_SKILL_DIR/.env.local" ]]; then
  echo "API key file preserved: $TARGET_SKILL_DIR/.env.local"
else
  echo "No API key file found. Create: $TARGET_SKILL_DIR/.env.local"
  echo 'Example: TWITTERAPI_IO_KEY=your_key_here'
fi
