#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Session Logger — SessionEnd hook
# ═══════════════════════════════════════════════════════════════════════════
# Logs completed sessions to a daily markdown file.
# Each line: time, topic (from first user message), session ID.
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ╔═══════════════════════════════════════════════════════════════╗
# ║  CUSTOMIZE: where to save session logs                       ║
# ╚═══════════════════════════════════════════════════════════════╝
LOG_DIR="$HOME/.claude/session-logs"
mkdir -p "$LOG_DIR"

TODAY=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/sessions-${TODAY}.md"

# Parse stdin JSON
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty')

# Exit if no transcript
[[ -n "$TRANSCRIPT" && -f "$TRANSCRIPT" ]] || exit 0

# Extract first user message as topic
TOPIC=$(grep '"type":"user"' "$TRANSCRIPT" 2>/dev/null | head -1 | \
    jq -r '.message.content |
        if type == "string" then .
        elif type == "array" then
            [.[] | select(.type == "text") | .text | select(contains("system-reminder") | not)] | join(" ")
        else empty end' 2>/dev/null | \
    head -c 80 | tr '\n' ' ' | sed 's/[[:space:]]*$//')

# Smart truncation
if [[ ${#TOPIC} -gt 60 ]]; then
    TOPIC="${TOPIC:0:60}"
    TOPIC="${TOPIC% *}…"
fi

[[ -z "$TOPIC" ]] && TOPIC="—"

# Create file header if new
if [[ ! -f "$LOG_FILE" ]]; then
    cat > "$LOG_FILE" << EOF
# Sessions – ${TODAY}

| Time | Topic | Session |
|------|-------|---------|
EOF
fi

# Append session
TIME=$(date +%H:%M)
echo "| ${TIME} | ${TOPIC} | \`${SESSION_ID:0:8}\` |" >> "$LOG_FILE"

exit 0
