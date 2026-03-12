#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Full Status Line with Project Presets + Mission Control
# ═══════════════════════════════════════════════════════════════════════════
# Features:
#   - Project-specific presets (router by directory)
#   - Task manager integration (reads state file)
#   - Background research indicator
#   - Mission Control JSON export for iTerm2/tmux
# ═══════════════════════════════════════════════════════════════════════════

read -r json
command -v jq &>/dev/null || { echo "▪ jq?"; exit 0; }

# ═══════════════════════════════════════════════════════════════════════════
# Parse JSON
# ═══════════════════════════════════════════════════════════════════════════

model=$(echo "$json" | jq -r '.model.display_name // "—"')
model_id=$(echo "$json" | jq -r '.model.id // ""')
project_dir=$(echo "$json" | jq -r '.workspace.project_dir // .cwd // ""')
ctx_used=$(echo "$json" | jq -r '.context_window.used_percentage // 0' | xargs printf "%.0f" 2>/dev/null || echo "0")
ctx_size=$(echo "$json" | jq -r '.context_window.context_window_size // 0')
cache_read=$(echo "$json" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
duration_ms=$(echo "$json" | jq -r '.cost.total_duration_ms // 0')

# Derived
duration_min=$((duration_ms / 60000))
cache_k=$((cache_read / 1000))
dir_name=$(basename "$project_dir" 2>/dev/null || echo "")

# Colors (optional — works in terminals that support ANSI)
RED=$'\033[0;31m'
DIM=$'\033[2m'
CYAN=$'\033[0;36m'
RESET=$'\033[0m'

# ═══════════════════════════════════════════════════════════════════════════
# Background research indicator
# ═══════════════════════════════════════════════════════════════════════════

RESEARCH_STATE="/tmp/claude-research-state.json"
research_seg=""
if [ -f "$RESEARCH_STATE" ]; then
    r_age=$(( $(date +%s) - $(stat -f %m "$RESEARCH_STATE" 2>/dev/null || echo 0) ))
    if [ "$r_age" -lt 1800 ]; then
        r_status=$(jq -r '.status // ""' < "$RESEARCH_STATE" 2>/dev/null)
        r_topic=$(jq -r '.topic // ""' < "$RESEARCH_STATE" 2>/dev/null | cut -c1-18)
        case "$r_status" in
            running) research_seg="${CYAN}◈${RESET} ${r_topic}…" ;;
            done)    research_seg="◉ ${r_topic} ✓" ;;
        esac
    fi
fi

# Model symbol
case "$model_id" in
    *opus*)   model_sym="◆" ;;
    *sonnet*) model_sym="■" ;;
    *haiku*)  model_sym="▪" ;;
    *)        model_sym="○" ;;
esac

# Progress bar (10 blocks)
progress_bar() {
    local pct=${1:-0}
    local filled=$(( (pct + 5) / 10 ))
    [ "$filled" -gt 10 ] && filled=10
    [ "$filled" -lt 0 ] && filled=0
    local empty=$((10 - filled))
    local bar=""
    for ((i=0; i<filled; i++)); do bar+="▰"; done
    for ((i=0; i<empty; i++)); do bar+="▱"; done
    echo "$bar"
}
ctx_bar=$(progress_bar "$ctx_used")

# ═══════════════════════════════════════════════════════════════════════════
# Task manager integration (reads from state file)
# ═══════════════════════════════════════════════════════════════════════════

task_seg=""
TASK_STATE="/tmp/claude-task-active.txt"
if [ -f "$TASK_STATE" ]; then
    task_id=$(cut -d'|' -f1 "$TASK_STATE" 2>/dev/null)
    [ -n "$task_id" ] && task_seg=" │ ◐${task_id}"
fi

# ═══════════════════════════════════════════════════════════════════════════
# PRESETS — customize per project
# ═══════════════════════════════════════════════════════════════════════════

preset_vault() {
    # Obsidian vault / notes
    local out="⏵ ${dir_name} │ ${model_sym} ${model} │ ${ctx_bar} ${ctx_used}%"
    [ "$cache_k" -gt 10 ] && out+=" ◇${cache_k}k"
    [ -n "$task_seg" ] && out+="${task_seg}"
    [ -n "$research_seg" ] && out+=" │ ${research_seg}"
    [ "$duration_min" -gt 0 ] && out+=" │ ${duration_min}m"
    echo -e "$out"
}

preset_code() {
    # Code project
    local out="${dir_name} │ ${model_sym} ${model} │ ${ctx_bar} ${ctx_used}%"
    [ "$cache_k" -gt 10 ] && out+=" ◇${cache_k}k"
    [ -n "$task_seg" ] && out+="${task_seg}"
    [ -n "$research_seg" ] && out+=" │ ${research_seg}"
    [ "$duration_min" -gt 0 ] && out+=" │ ${duration_min}m"
    echo -e "$out"
}

preset_generic() {
    local out="${dir_name} │ ${model_sym} ${model} │ ${ctx_bar} ${ctx_used}%"
    [ "$cache_k" -gt 10 ] && out+=" ◇${cache_k}k"
    [ "$duration_min" -gt 0 ] && out+=" │ ${duration_min}m"
    echo "$out"
}

# ═══════════════════════════════════════════════════════════════════════════
# Mission Control — write JSON state for iTerm2/tmux
# ═══════════════════════════════════════════════════════════════════════════

MC_DIR="$HOME/.config/iterm2-mission-control"
[ -d "$MC_DIR" ] || mkdir -p "$MC_DIR"
left_k=$(( ctx_size * (100 - ctx_used) / 100000 ))

printf '{"percent":%d,"left_k":%d,"cache_k":%d,"model":"%s","project":"%s","duration_min":%d,"ts":%d}\n' \
    "$ctx_used" "$left_k" "$cache_k" "$model" "$dir_name" "$duration_min" "$(date +%s)" \
    > "$MC_DIR/context.json" 2>/dev/null

# ═══════════════════════════════════════════════════════════════════════════
# ROUTER — detect project and call preset
# ═══════════════════════════════════════════════════════════════════════════
# Customize these patterns for your directory structure

case "$project_dir" in
    */notes*|*/vault*|*/obsidian*)
        preset_vault
        ;;
    */_code/*|*/projects/*)
        preset_code
        ;;
    *)
        preset_generic
        ;;
esac
