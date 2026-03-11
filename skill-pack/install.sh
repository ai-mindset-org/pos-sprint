#!/bin/bash
# POS Starter Pack — CTRL
# Install all 4 skills to ~/.claude/skills/

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude/skills"

echo "ctrl > installing POS Starter Pack..."
echo ""

installed=0
for skill_dir in "$SCRIPT_DIR"/pos-*/; do
  skill_name=$(basename "$skill_dir")
  if [ -f "$skill_dir/SKILL.md" ]; then
    mkdir -p "$TARGET/$skill_name"
    cp "$skill_dir/SKILL.md" "$TARGET/$skill_name/SKILL.md"
    echo "  + /$skill_name"
    installed=$((installed + 1))
  fi
done

echo ""
echo "ctrl > $installed skills installed to $TARGET"
echo ""
echo "try:"
echo "  /pos-audit         — scan your POS"
echo "  /pos-morning       — daily brief"
echo "  /pos-dashboard-gen — generate dashboard"
echo "  /pos-skill-factory — create new skills"
