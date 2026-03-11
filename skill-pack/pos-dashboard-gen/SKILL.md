---
name: pos-dashboard-gen
description: Generate a personal HTML dashboard from your POS context. Auto-detects MCP, gathers data, builds terminal-aesthetic single-file page.
version: 3.0
user_invocable: true
arguments:
  - name: panels
    description: "Comma-separated: focus,calendar,tasks,sessions,skills,docs,metrics (default: all available)"
    required: false
  - name: theme
    description: "dark (default) or light"
    required: false
  - name: output
    description: "Output path (default: /tmp/pos-dashboard.html)"
    required: false
---

# POS Dashboard Generator

Generate a self-contained HTML dashboard from your POS context. Auto-detects integrations, gathers data, builds a single-file page with terminal aesthetic. Snapshot at generation time — run again to refresh.

## Step 0: Detect Integrations

Same pattern as `/pos-morning` — read MCP config first:

```bash
cat ~/.claude/mcp.json 2>/dev/null
```

Also check local tools:

```bash
# Calendar script
[ -x "$HOME/.claude/scripts/gcal-smart.sh" ] && echo "gcal: available"

# Linear cache
find ~/.claude/projects -name "linear-tracking.md" -type f 2>/dev/null | head -1
```

Build source map. Only gather from detected sources.

## Step 1: Gather Data

For each panel, fetch data. **Skip panels without data** — empty panel is worse than no panel.

### Focus Panel
Sources (try in order):
1. Today's focus from recent `/pos-morning` output or daily-focus file
2. Memory files: `find ~/.claude/projects -name "MEMORY.md" -type f 2>/dev/null`
3. CLAUDE.md project description
4. Fallback: "run /pos-morning to set today's focus"

### Calendar Panel
**Degradation chain:**
1. Krisp MCP: `ToolSearch: "+krisp meetings"` → `mcp__krisp__list_upcoming_meetings`
2. gcal script: `"$HOME/.claude/scripts/gcal-smart.sh" today`
3. Skip panel

Format: `[{time: "10:00", title: "Standup", duration: "30m"}]`

### Tasks Panel
**Degradation chain:**
1. Linear MCP: `ToolSearch: "+linear list_issues"` → `mcp__linear__list_issues(assignee: "me", status: "started")`
2. Linear cache: read `linear-tracking.md`
3. Local TODO: `find . -maxdepth 2 -name "TODO.md" 2>/dev/null`
4. Skip panel

Format: `[{id: "AIM-123", title: "Task", priority: "high", status: "IP"}]`

### Sessions Panel
```bash
touch -t $(date +%Y%m%d)0000 /tmp/pos-today-marker 2>/dev/null
find ~/.claude/projects -name "*.jsonl" -newer /tmp/pos-today-marker -maxdepth 3 2>/dev/null | head -8
```

For each: project (path), first user message (topic), line count (activity).

### Skills Panel
```bash
ls ~/.claude/skills/*/SKILL.md 2>/dev/null
ls ~/.claude/skills/*.md 2>/dev/null
ls .claude/skills/*/SKILL.md 2>/dev/null
```

Extract names from paths.

### Documents Panel
```bash
find . -name "*.md" -mmin -720 \
  -not -path "./.obsidian/*" \
  -not -path "./.trash/*" \
  -not -path "./node_modules/*" \
  2>/dev/null | head -8
```

### Metrics Panel
Computed from gathered data:
- `sessions`: today's session count
- `tasks_ip`: in-progress tasks
- `tasks_todo`: todo tasks
- `skills`: installed skill count
- `files_today`: recently modified files
- `mcp_servers`: configured server count

## Step 2: Build HTML

Generate a **single self-contained HTML file**.

### CSS Design System

```css
:root {
  --bg: #0d1117;
  --bg2: #161b22;
  --bg3: #1c2128;
  --border: rgba(48, 54, 61, 0.6);
  --accent: #55aa88;
  --accent-dim: #3d8066;
  --blue: #4488cc;
  --amber: #d4a843;
  --red: #cc4444;
  --text: #c9d1d9;
  --text-dim: #8b949e;
  --text-bright: #e6edf3;
  --mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', monospace;
  --r: 6px;
}

.light {
  --bg: #ffffff;
  --bg2: #f6f8fa;
  --bg3: #f0f2f5;
  --border: #d0d7de;
  --accent: #2d8659;
  --text: #1f2328;
  --text-dim: #656d76;
  --text-bright: #1f2328;
}
```

### Layout

```
┌─ Terminal Strip (scrolling log) ────────────────┐
├─ Header: POS DASHBOARD · {date} · LIVE {clock} ─┤
├──────────────────────────────────────────────────┤
│ Focus     │ Calendar   │ Tasks      │ Skills     │
├───────────┼────────────┼────────────┼────────────┤
│ Sessions  │ Documents  │ Metrics    │            │
└──────────────────────────────────────────────────┘
```

Grid: `grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))`

### Terminal Strip

Scrolling CSS marquee with real data:

```html
<div class="terminal-strip">
  <div class="strip-scroll">
    {time} pos-morning ✓ · {time} linear sync {n} tasks ·
    {time} session started · {time} vault: {n} files ·
  </div>
</div>
```

CSS: `animation: scroll-left 30s linear infinite`

### Panel Template

```html
<div class="panel" data-panel="{name}">
  <div class="panel-head">
    <span class="panel-icon">></span>
    <span class="panel-title">{NAME}</span>
    <span class="panel-badge">{count}</span>
  </div>
  <div class="panel-body"><!-- items --></div>
</div>
```

Styles:
- `panel-head`: uppercase, border-bottom accent, `font-size: 0.72rem`
- `panel-body`: 12px padding, `font-size: 0.8rem`
- `panel-badge`: pill, accent background

### Data Injection

Embed as JS constants:

```javascript
const POS = {
  generated: "{ISO timestamp}",
  theme: "{dark|light}",
  focus: "{focus sentence}",
  calendar: [{time, title, duration}],
  tasks: [{id, title, priority, status}],
  sessions: [{project, topic, lines, time}],
  skills: ["{name}", ...],
  docs: [{name, modified}],
  metrics: {sessions, tasks_ip, tasks_todo, skills, files_today, mcp_servers}
};
```

### Panel Rendering

**Focus**: large text, accent color, full-width top.
**Calendar**: time-sorted, `{time}` monospace dim, `{title}` bright.
**Tasks**: priority dot (red=urgent, amber=high, blue=medium, dim=low), `{id}` dim prefix. Group by status.
**Sessions**: `{time}` dim, `{project}` accent, `{topic}` text, activity bar (thin inline proportional to lines).
**Skills**: chip grid. Click copies `/{name}` to clipboard.
**Documents**: filename + "modified {ago}" dim.
**Metrics**: 2x3 grid, big accent numbers, labels below.

### Must-Have Features

- **Live clock**: `setInterval` every 30s in header
- **Terminal strip**: CSS marquee with real data
- **Monospace**: JetBrains Mono from Google Fonts (with system fallback)
- **Skill chips**: click-to-copy skill name
- **Priority dots**: colored circles for tasks
- **No external JS**: everything inline
- **Google Fonts fallback**: works without CDN

### Size Target

400-700 lines. Fewer panels → shorter file.

## Step 3: Write and Open

```bash
OUTPUT="${output:-/tmp/pos-dashboard.html}"
```

Write with Write tool, then:

```bash
open "$OUTPUT"
```

Show:

```
dashboard generated

  path: {output}
  panels: {included list}
  data: {summary of sources}
  theme: {dark|light}

  → open {output}
```

## Principles

- **Snapshot**: static at generation time — run again to refresh
- **Zero runtime deps**: Google Fonts optional (degrades to system mono)
- **Terminal aesthetic**: dark bg, green accent, monospace, box-drawing
- **Portable**: share as file, open on any machine with browser
- **Data-driven panels**: no data = no panel (skip entirely)
- **Single file**: CSS, JS, data, fonts fallback — all inline

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Rendering empty panels | No data = skip panel entirely |
| External JS/CSS | Everything inline in single file |
| Hardcoded personal data | All data from POS context gathering |
| Fixed grid breaking mobile | `auto-fit, minmax(280px, 1fr)` |
| 1000+ line HTML | Target 400-700 lines |
| Missing font fallback | System monospace in font stack always |
| Live fetch in HTML | Snapshot only — no XHR/fetch calls |
| Forgetting live clock | `setInterval` updating header every 30s |
