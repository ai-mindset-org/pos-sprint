---
name: pos-morning
description: Morning pipeline — calendar + tasks + recent work → daily brief. Works with any Claude Code setup. No MCP required.
version: 1.0
user_invocable: true
arguments:
  - name: style
    description: "Output style: brief (default), full, telegram"
    required: false
---

# POS Morning — Daily Brief Pipeline

Generate a morning brief by aggregating your context: calendar, tasks, recent sessions, and vault state.

## How it works

1. **Gather context** from available sources (adapts to what you have)
2. **Synthesize** into a focused daily brief
3. **Output** in chosen format

## Step 1: Gather Context

Try each source. Skip silently if unavailable.

### Calendar
```bash
# Try gcal-smart.sh if exists
GCAL_SCRIPTS=(
  "$HOME/Library/CloudStorage/Dropbox/notes/code tools/mcp-scripts/gcal-smart.sh"
  "$HOME/.claude/scripts/gcal.sh"
)
for script in "${GCAL_SCRIPTS[@]}"; do
  [ -x "$script" ] && "$script" today && break
done
```
If no script exists, check if Krisp MCP is available:
- `mcp__krisp__list_upcoming_meetings` — today's meetings

If nothing works, skip calendar and note "no calendar connected".

### Tasks
Try in order:
1. **Linear MCP**: `mcp__linear__list_issues(assignee: "me", state: "In Progress")` + state "Todo"
2. **Linear cache file**: Read `~/.claude/projects/*/memory/linear-tracking.md`
3. **Local TODO files**: Search for `TODO.md`, `tasks.md` in working directory
4. Skip if nothing found.

### Recent Work
```bash
# Find today's Claude Code sessions
find ~/.claude/projects -name "*.jsonl" -newer /tmp/today-marker -maxdepth 3 2>/dev/null | head -5
```
Or use the sessions skill pattern: read recent JSONL files, extract topics.

### Vault State (optional)
If working directory contains markdown files:
```bash
# Recently modified files (last 12 hours)
find . -name "*.md" -mmin -720 -not -path "./.obsidian/*" -not -path "./.trash/*" | head -10
```

## Step 2: Synthesize

Combine all gathered context into a brief. Structure:

```
┌─────────────────────────────────────────────────┐
│  MORNING BRIEF · {weekday} {date}               │
└─────────────────────────────────────────────────┘

  FOCUS
  > {main priority — 1 sentence derived from tasks + calendar}

  CALENDAR ({count} events)
  ├─ {time}  {event title}
  ├─ {time}  {event title}
  └─ {time}  {event title}

  TASKS ({count} in progress)
  ├─ {id}  {title}                           {priority}
  ├─ {id}  {title}                           {priority}
  └─ {id}  {title}                           {priority}

  YESTERDAY
  > {1-2 sentences: what you worked on based on recent sessions}

  OBSERVATIONS
  · {insight about today's schedule — conflicts, gaps, patterns}
  · {suggestion based on overdue tasks or upcoming deadlines}
```

## Step 3: Output Format

### brief (default)
The format above, printed to terminal.

### full
Same as brief + add section:
```
  RECENT FILES
  ├─ {filename}  {modified time}
  └─ {filename}  {modified time}
```

### telegram
Compact version for Telegram (if telegram MCP available):
```
#morning {weekday}

focus: {main priority}

{time} {event}
{time} {event}

tasks: {count} IP
· {most important task}
· {second task}

> {one observation}
```
Send via `mcp__telegram__telegram_send_self` (Saved Messages).

## Principles

- **Graceful degradation**: works with 0 integrations (just gives empty sections) up to full stack
- **No setup required**: adapts to whatever MCP servers and scripts are available
- **Opinionated focus**: always suggest ONE main focus derived from all context
- **Fast**: should complete in under 30 seconds
