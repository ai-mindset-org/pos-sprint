---
name: pos-dashboard-gen
description: Generate a personal HTML dashboard from your POS context. Single-file, no server needed. Opens in browser.
version: 1.0
user_invocable: true
arguments:
  - name: panels
    description: "Comma-separated panels to include: focus,calendar,tasks,sessions,skills,docs,metrics,telegram (default: all available)"
    required: false
  - name: theme
    description: "dark (default) or light"
    required: false
  - name: output
    description: "Output path (default: /tmp/pos-dashboard.html)"
    required: false
---

# POS Dashboard Generator

Generate a self-contained HTML dashboard from your current POS context. No server needed — opens directly in browser. Data is snapshot (static), refreshed each time you run the skill.

## How it works

1. **Gather data** from available sources
2. **Build HTML** with terminal aesthetic
3. **Write file** and open in browser

## Step 1: Gather Data

For each panel, try to fetch data. Skip panels where data is unavailable.

### Focus
- Read focus file: search for today's date in `daily-focus` files
- Or extract from CLAUDE.md project description
- Fallback: "run /pos-morning to set focus"

### Calendar
```bash
# Try gcal script
GCAL="$HOME/Library/CloudStorage/Dropbox/notes/code tools/mcp-scripts/gcal-smart.sh"
[ -x "$GCAL" ] && "$GCAL" today
```
Or: `mcp__krisp__list_upcoming_meetings`
Format: `[{time, title}]`

### Tasks
- Linear MCP: `list_issues(assignee: "me", state: "In Progress")`
- Or: read `linear-tracking.md` from memory
- Format: `[{id, title, priority}]`

### Sessions
```bash
# Today's sessions from JSONL logs
TODAY=$(date +%Y-%m-%d)
find ~/.claude/projects -name "*.jsonl" -newer /tmp/today-marker 2>/dev/null
```
Extract: session ID, project, topic, tool count, start time.

### Skills
```bash
ls ~/.claude/skills/*/SKILL.md 2>/dev/null | sed 's|.*/\(.*\)/SKILL.md|\1|'
ls .claude/skills/*/SKILL.md 2>/dev/null | sed 's|.*/\(.*\)/SKILL.md|\1|'
```

### Documents
```bash
# Recently modified markdown files
find . -name "*.md" -mmin -720 -not -path "./.obsidian/*" 2>/dev/null | head -8
```

### Metrics
Computed from other data:
- Session count
- Task count
- Skill count
- Files modified today

## Step 2: Build HTML

Generate a single HTML file with these specs:

### Design System

```css
:root {
  --bg: #0d1117;
  --bg2: #161b22;
  --border: rgba(48, 54, 61, 0.6);
  --accent: #55aa88;
  --blue: #4488cc;
  --amber: #d4a843;
  --red: #cc4444;
  --text: #c9d1d9;
  --text-dim: #8b949e;
  --text-bright: #e6edf3;
  --mono: 'JetBrains Mono', 'SF Mono', monospace;
}
```

For light theme: invert to white bg, dark text.

### Layout

```
┌─ Terminal Strip (scrolling logs) ──────────────────┐
├─ Header: logo + "POS LIVE" badge + clock ──────────┤
├────────────────────────────────────────────────────┤
│ Focus    │ Timeline  │ Tasks     │ Skills          │
│ Calendar │ Sessions  │ Telegram  │ Documents       │
│ Metrics  │           │           │                 │
└────────────────────────────────────────────────────┘
```

Grid: `grid-template-columns: 220px 1fr 1fr 220px`
Responsive: collapse to 2 cols at 1100px, 1 col at 700px.

### Panel Template

Each panel follows this HTML pattern:

```html
<div class="panel">
  <div class="panel-header">
    <span class="panel-icon">&gt;</span>
    <span class="panel-title">Focus</span>
    <span class="panel-badge">{count}</span>
  </div>
  <div class="panel-body">
    <!-- content -->
  </div>
</div>
```

### Data Injection

Embed gathered data as JavaScript constants at the top of `<script>`:

```javascript
const DATA = {
  focus: { main: "...", items: [...] },
  calendar: [...],
  tasks: [...],
  sessions: [...],
  skills: [...],
  docs: [...],
  metrics: {...}
};
```

### Must-have features

- **Live clock** updating every 30s
- **Terminal strip** at top with scrolling log entries
- **Monospace everything** (JetBrains Mono from Google Fonts)
- **Skill chips** are clickable (copy skill name to clipboard)
- **Session rows** show time, project, topic, tool count
- **Task rows** show priority dot, ID, title

## Step 3: Write and Open

```bash
# Write the file
# Default: /tmp/pos-dashboard.html
# Or user-specified path

# Open in browser
open {output_path}
```

## Principles

- **Snapshot, not live**: Data is static at generation time. Run again to refresh.
- **Zero dependencies at runtime**: Google Fonts CDN is the only external resource (and it degrades gracefully to system monospace)
- **Terminal aesthetic**: Dark theme, green accent, monospace, box-drawing characters
- **Portable**: Can be shared as a file, opened on any machine with a browser
- **Minimal code**: The generated HTML should be 400-600 lines, not more
