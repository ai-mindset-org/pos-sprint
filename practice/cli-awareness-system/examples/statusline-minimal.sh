#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Minimal Status Line for Claude Code
# ═══════════════════════════════════════════════════════════════════════════
# Shows: project │ model │ context bar │ duration
# Install: chmod +x ~/.claude/statusline.sh
# Config:  "statusLine": { "type": "command", "command": "~/.claude/statusline.sh" }
# ═══════════════════════════════════════════════════════════════════════════

read -r json
command -v jq &>/dev/null || { echo "▪ jq?"; exit 0; }

# Parse JSON
model=$(echo "$json" | jq -r '.model.display_name // "—"')
model_id=$(echo "$json" | jq -r '.model.id // ""')
project_dir=$(echo "$json" | jq -r '.workspace.project_dir // .cwd // ""')
ctx_used=$(echo "$json" | jq -r '.context_window.used_percentage // 0' | xargs printf "%.0f" 2>/dev/null)
cache_read=$(echo "$json" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
duration_ms=$(echo "$json" | jq -r '.cost.total_duration_ms // 0')

dir_name=$(basename "$project_dir" 2>/dev/null)
cache_k=$((cache_read / 1000))
duration_min=$((duration_ms / 60000))

# Model symbol
case "$model_id" in
    *opus*)   model_sym="◆" ;;
    *sonnet*) model_sym="■" ;;
    *haiku*)  model_sym="▪" ;;
    *)        model_sym="○" ;;
esac

# Progress bar (10 blocks)
filled=$(( (ctx_used + 5) / 10 ))
[ "$filled" -gt 10 ] && filled=10
[ "$filled" -lt 0 ] && filled=0
bar=""
for ((i=0; i<filled; i++)); do bar+="▰"; done
for ((i=filled; i<10; i++)); do bar+="▱"; done

# Output
out="${dir_name} │ ${model_sym} ${model} │ ${bar} ${ctx_used}%"
[ "$cache_k" -gt 10 ] && out+=" ◇${cache_k}k"
[ "$duration_min" -gt 0 ] && out+=" │ ${duration_min}m"
echo "$out"
