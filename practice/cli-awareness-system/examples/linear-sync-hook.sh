#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# Task Awareness — SessionStart hook
# ═══════════════════════════════════════════════════════════════════════════
# Reads cached tasks from memory file and outputs context for Claude.
# Works with any task manager — just change the memory file format.
# Target: <200ms (no API calls, memory file only).
# ═══════════════════════════════════════════════════════════════════════════

set -eo pipefail

# ╔═══════════════════════════════════════════════════════════════╗
# ║  CUSTOMIZE: path to your task cache file                     ║
# ╚═══════════════════════════════════════════════════════════════╝
MEMORY_FILE="$HOME/.claude/projects/YOUR-PROJECT/memory/task-tracking.md"

# Exit silently if no memory file
[[ -f "$MEMORY_FILE" ]] || exit 0
[[ -s "$MEMORY_FILE" ]] || exit 0

CONTENT=$(<"$MEMORY_FILE")

# ═══════════════════════════════════════════════════════════════════════════
# Extract active tasks
# ═══════════════════════════════════════════════════════════════════════════
# Format: #### TASK-ID · Description · Status
# Example: #### AIM-123 · Fix login bug · IP

ACTIVE_TASKS=()
while IFS= read -r line; do
    task="${line#\#\#\#\# }"
    ACTIVE_TASKS+=("$task")
done < <(echo "$CONTENT" | grep -E '^#### .+ · (IP|In Progress)$' | head -10)

ACTIVE_COUNT=${#ACTIVE_TASKS[@]}
[[ $ACTIVE_COUNT -gt 0 ]] || exit 0

# ═══════════════════════════════════════════════════════════════════════════
# Staleness check
# ═══════════════════════════════════════════════════════════════════════════

UPDATED=$(echo "$CONTENT" | grep -m1 '^updated:' | sed 's/^updated:[[:space:]]*//' || true)
STALE_WARNING=""

if [[ -n "$UPDATED" ]]; then
    UPDATED_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M" "$UPDATED" "+%s" 2>/dev/null || echo "0")
    NOW_EPOCH=$(date "+%s")
    if [[ "$UPDATED_EPOCH" -gt 0 ]]; then
        AGE_HOURS=$(( (NOW_EPOCH - UPDATED_EPOCH) / 3600 ))
        [[ $AGE_HOURS -gt 4 ]] && STALE_WARNING="⚠ cache stale (${AGE_HOURS}h) — sync recommended"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# Write active task to state file (for statusline)
# ═══════════════════════════════════════════════════════════════════════════

STATE_FILE="/tmp/claude-task-active.txt"
FIRST_TASK="${ACTIVE_TASKS[0]}"
TASK_ID=$(echo "$FIRST_TASK" | grep -oE '[A-Z]+-[0-9]+' | head -1)
TASK_DESC=$(echo "$FIRST_TASK" | sed -E 's/^[A-Z]+-[0-9]+ · //' | sed -E 's/ · (IP|In Progress)$//')

if [[ -n "$TASK_ID" ]]; then
    echo "${TASK_ID}|${TASK_DESC}" > "$STATE_FILE"
fi

# ═══════════════════════════════════════════════════════════════════════════
# Output for Claude context
# ═══════════════════════════════════════════════════════════════════════════

echo "--- Task Awareness Layer ---"
echo "Active tasks: ${ACTIVE_COUNT}"

for task in "${ACTIVE_TASKS[@]}"; do
    echo "  ${task}"
done

[[ -n "$STALE_WARNING" ]] && echo "$STALE_WARNING"

echo "--- End Tasks ---"
exit 0
