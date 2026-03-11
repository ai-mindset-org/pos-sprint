#!/bin/bash
# POS Starter Pack — CTRL v3
# Install all 5 skills to ~/.claude/skills/

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude/skills"

echo "ctrl > installing POS Starter Pack v3..."
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
echo "start here:"
echo "  /pos-setup         — build POS from zero (6-phase pipeline)"
echo ""
echo "or jump to:"
echo "  /pos-audit         — scan and score your setup (0-12)"
echo "  /pos-morning       — daily brief with focus sentence"
echo "  /pos-dashboard-gen — terminal-aesthetic HTML dashboard"
echo "  /pos-skill-factory — create skills from ideas"
