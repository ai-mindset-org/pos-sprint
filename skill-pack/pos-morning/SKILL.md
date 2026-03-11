---
name: pos-morning
description: Morning brief pipeline — auto-detects MCP servers, gathers calendar + tasks + sessions + vault, synthesizes ONE focus sentence. Three output modes.
version: 3.0
user_invocable: true
arguments:
  - name: style
    description: "Output: brief (default), full, telegram"
    required: false
---

# POS Morning — Daily Brief Pipeline

Generate a morning brief by auto-detecting your integrations, gathering context from every available source, and synthesizing ONE focused sentence for the day. Works with zero setup — adapts to whatever you have connected.

This is the **"aha moment"** of a POS — the first time all your data sources produce a single actionable priority.

## Step 0: Detect Available Integrations

Read MCP config to know what's available BEFORE gathering data:

```bash
cat ~/.claude/mcp.json 2>/dev/null
```

Build integrations map from configured servers:

| Server | Capability | Loader |
|--------|-----------|--------|
| krisp | Meetings, transcripts, action items | `ToolSearch: "+krisp"` |
| linear | Tasks, projects, sprints | `ToolSearch: "+linear list"` |
| telegram | Saved messages (context clues) | `ToolSearch: "+telegram get"` |
| notion | Notes, databases | `ToolSearch: "+notion search"` |
| exa | Web context (optional) | `ToolSearch: "+exa"` |

**Only ToolSearch servers found in mcp.json.** Don't guess — if not configured, don't try.

Also check for local tools:

```bash
# Google Calendar script (bash wrapper)
GCAL_SCRIPTS=("$HOME/.claude/scripts/gcal-smart.sh" "$HOME/.claude/scripts/gcal.sh")
for s in "${GCAL_SCRIPTS[@]}"; do [ -x "$s" ] && echo "gcal: $s" && break; done

# Linear tracking cache (memory file)
find ~/.claude/projects -name "linear-tracking.md" -type f 2>/dev/null | head -1
```

## Step 1: Gather Context

Try each source in degradation order. **Skip silently** if unavailable — never error, never ask to install.

### 1.1 Calendar

**Degradation chain** (stop at first success):

1. **Krisp MCP** (if in mcp.json):
   ```
   ToolSearch: "+krisp meetings"
   mcp__krisp__list_upcoming_meetings
   mcp__krisp__search_meetings  (yesterday, for recap)
   ```
   Krisp also provides action items from yesterday's meetings — extract these.

2. **Google Calendar script**:
   ```bash
   "$HOME/.claude/scripts/gcal-smart.sh" today
   "$HOME/.claude/scripts/gcal-smart.sh" week  # for broader context
   ```

3. **Skip** — note "no calendar" in output header.

### 1.2 Tasks

**Degradation chain:**

1. **Linear MCP**:
   ```
   ToolSearch: "+linear list_issues"
   mcp__linear__list_issues(assignee: "me", status: "started")
   mcp__linear__list_issues(assignee: "me", status: "unstarted")
   ```
   Also check for recently completed (last 3 days) to show momentum.

2. **Linear cache** (memory file):
   ```bash
   TRACKING=$(find ~/.claude/projects -name "linear-tracking.md" -type f 2>/dev/null | head -1)
   ```
   Read and extract cached task list with statuses.

3. **Local TODO**:
   ```bash
   find . -maxdepth 2 \( -name "TODO.md" -o -name "tasks.md" -o -name "TODO" \) 2>/dev/null | head -3
   ```

4. **Skip** — note "no task source".

### 1.3 Messages (context clues)

**Only if Telegram MCP detected:**

```
ToolSearch: "+telegram get_messages"
mcp__telegram__telegram_get_messages(dialog: "me", limit: 5)
```

Saved messages reveal what the user was thinking about. Extract themes, don't display raw messages.

### 1.4 Recent Sessions

```bash
touch -t $(date +%Y%m%d)0000 /tmp/pos-today-marker 2>/dev/null
find ~/.claude/projects -name "*.jsonl" -newer /tmp/pos-today-marker -maxdepth 3 2>/dev/null | head -5

# If nothing today, check yesterday
YESTERDAY=$(date -v-1d +%Y%m%d 2>/dev/null || date -d "yesterday" +%Y%m%d 2>/dev/null)
touch -t ${YESTERDAY}0000 /tmp/pos-yesterday-marker 2>/dev/null
find ~/.claude/projects -name "*.jsonl" -newer /tmp/pos-yesterday-marker -maxdepth 3 2>/dev/null | head -5
```

For each session, read first 20 and last 20 lines to extract:
- Project name (from path)
- Topic (from first user message)
- Tools used (count of tool calls, approximate effort)

### 1.5 Vault State (optional)

If working directory is a vault:

```bash
find . -name "*.md" -mmin -720 \
  -not -path "./.obsidian/*" \
  -not -path "./.trash/*" \
  -not -path "./.smart-env/*" \
  -not -path "./node_modules/*" \
  2>/dev/null | head -10
```

### 1.6 Yesterday's Meetings (if Krisp available)

```
mcp__krisp__search_meetings (yesterday's date range)
mcp__krisp__list_activities
```

Extract per-meeting:
- Title, duration, participants
- Action items generated
- Talk time ratio (were you presenting or listening?)

## Step 2: Synthesize

### Weekday-aware mode

Adjust synthesis by day:

| Day | Mode | Extra |
|-----|------|-------|
| Monday | Week overview | Show full week calendar, sprint status |
| Tuesday-Thursday | Standard | Focus on today's blocks |
| Friday | Wins + lessons | Show completed tasks this week, retrospective prompt |

### FOCUS derivation

The single most important output. Derive ONE sentence from ALL context:

1. Check today's calendar — what's the biggest time commitment?
2. Check in-progress tasks — what's most urgent or overdue?
3. Check yesterday's sessions — what was the user mid-work on?
4. Check action items from yesterday's meetings — what was promised?
5. Combine: **"[Action verb] [specific thing] [by when / why]"**

Examples:
- "Finalize workshop slides before 14:00 session"
- "Close 3 overdue Linear tasks — sprint ends Friday"
- "No meetings today — deep work on dashboard generator"
- "Follow up on partnership call action items before standup"

**NEVER** generic focus like "have a productive day" — must be specific.

### Output structure

```
┌─────────────────────────────────────────────────┐
│  MORNING BRIEF · {weekday} {date}               │
│  sources: {list of what connected}              │
└─────────────────────────────────────────────────┘

  FOCUS
  > {main priority — 1 sentence from all context}

  CALENDAR ({count} events)
  ├─ {time}  {title}  ({duration})
  ├─ {time}  {title}  ({duration})
  └─ {time}  {title}  ({duration})

  TASKS ({in_progress} IP · {todo} todo)
  ├─ {id}  {title}                           ◐ IP
  ├─ {id}  {title}                           ◐ IP
  └─ +{N} in backlog

  YESTERDAY
  > {1-2 sentences: what you worked on, based on sessions + meetings}

  OBSERVATIONS
  · {schedule insight — conflicts, free blocks, back-to-back}
  · {task insight — overdue items, approaching deadlines}
  · {pattern — "3 sessions on X this week, close it today?"}
```

## Step 3: Output Modes

### brief (default)
Terminal output as above.

### full
Same + additional sections:

```
  YESTERDAY'S MEETINGS ({count})
  ├─ {title}  {duration}  {participants}
  │  → action: {item}
  └─ {title}  {duration}

  RECENT FILES ({count})
  ├─ {filename}  {modified time ago}
  └─ {filename}  {modified time ago}

  SAVED MESSAGES
  ├─ {preview of recent telegram saved}
  └─ {preview}

  INTEGRATIONS
  ├─ calendar     {krisp|gcal|none}
  ├─ tasks        {linear|cache|local|none}
  ├─ messaging    {telegram|none}
  ├─ meetings     {krisp|none}
  └─ sessions     {N found}
```

### telegram
Compact version for Telegram Saved Messages:

```
#morning {weekday}

focus: {priority}

{time} {event}
{time} {event}

tasks: {count} IP · {count} todo
· {most important}
· {second}

> {one observation}
```

Send via:
```
ToolSearch: "+telegram send_self"
mcp__telegram__telegram_send_self(message: "{brief}")
```

If Telegram not available, fall back to `brief` and note it.

## Principles

- **Graceful degradation**: 0 integrations = minimal brief; full stack = rich brief
- **Never error on missing source**: skip silently, note what connected in header
- **Opinionated focus**: ALWAYS synthesize ONE focus — this is the core value
- **Fast**: direct tool calls only, no background agents needed, <30 seconds
- **Weekday-aware**: Monday overview, Friday retrospective, standard midweek
- **Action items carry forward**: yesterday's meeting commitments appear in today's brief

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| ToolSearch for server not in mcp.json | Only search servers found in config |
| Generic focus: "be productive today" | Focus MUST be specific: action + object + deadline |
| Showing raw JSONL content | Extract topic from first user message only |
| Failing when no calendar | Skip silently — brief with just tasks is valuable |
| Hardcoded MCP tool names | ToolSearch first — tool names vary across setups |
| Sending telegram without checking | Check Step 0 map — only send if detected |
| Reading entire session files | First 20 + last 20 lines is enough for topic |
| Skipping yesterday's meetings | Krisp action items are tomorrow's priorities |
