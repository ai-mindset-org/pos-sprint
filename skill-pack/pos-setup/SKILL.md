---
name: pos-setup
description: Build your Personal Operating System from zero — 6-phase pipeline with real MCP integrations, hooks, and operational layer.
version: 3.0
user_invocable: true
arguments:
  - name: phase
    description: "Jump to phase: context, mcp, skills, hooks, ops, dashboard (default: auto-detect)"
    required: false
---

# POS Setup — Build Your Personal Operating System

Sequential pipeline that builds a working Personal Operating System from zero. Auto-detects what you already have, skips completed phases, guides through each layer. Based on real production setup patterns — not generic templates.

**The 6 layers of a POS:**
1. **Context** (CLAUDE.md) — persistent identity, rules, conventions
2. **MCP** — data source connections (calendar, tasks, search, messaging)
3. **Skills** — reusable workflows as markdown files
4. **Hooks** — automation triggers (session start/end, file writes)
5. **Operations** — daily rituals, ambient tracking, quality systems
6. **Dashboard** — visual snapshot of your system

## Phase 0: State Detection

Before starting, check what exists:

```bash
CLAUDE_GLOBAL=$([ -f ~/.claude/CLAUDE.md ] && wc -l < ~/.claude/CLAUDE.md || echo 0)
CLAUDE_PROJECT=$([ -f ./CLAUDE.md ] && echo "yes" || echo "no")
MCP_SERVERS=$(cat ~/.claude/mcp.json 2>/dev/null | grep -c '"command"\|"url"' || echo 0)
SKILLS_COUNT=$(ls ~/.claude/skills/*/SKILL.md ~/.claude/skills/*.md 2>/dev/null | wc -l)
HOOKS_SET=$([ -f ~/.claude/hooks.json ] && echo "yes" || echo "no")
MEMORY_FILES=$(find ~/.claude/projects -name "MEMORY.md" 2>/dev/null | wc -l)
DASHBOARD=$([ -f /tmp/pos-dashboard.html ] && echo "exists" || echo "none")
```

Show state map:

```
  POS STATE
  ├─ context      {CLAUDE_GLOBAL}L global · project: {yes|no}
  ├─ mcp          {MCP_SERVERS} servers
  ├─ skills       {SKILLS_COUNT} installed
  ├─ hooks        {yes|no}
  ├─ operations   memory: {MEMORY_FILES} projects
  └─ dashboard    {exists|none}

  starting from: phase {first incomplete}
```

**Phase thresholds** (skip if met):
- context: CLAUDE.md > 30 lines with named sections
- mcp: 3+ servers across 2+ categories
- skills: 5+ skills installed
- hooks: hooks.json exists with 1+ hook
- ops: memory active across 2+ projects
- dashboard: file exists and < 24h old

If `{phase}` argument provided, jump directly.

## Phase 1: Context Assembly

**Goal**: create `~/.claude/CLAUDE.md` — your persistent identity layer.

This file loads into EVERY session. It defines rules, naming, integrations, and workflows.

**If exists and > 30 lines**: read it, show sections found, ask to extend. Skip if user declines.

**If missing or thin**: ask via `AskUserQuestion`:

```
What level of context do you need?

1. Starter — formatting + naming convention + tool preferences
2. Professional — add work context, team, integrations, communication style
3. Full system — add eval protocol, context management, Linear awareness, hooks
```

### Starter template (write with Write tool):

```markdown
# Claude Code Rules

## Formatting
- **Bold** for key concepts
- Clear headers for sections
- Monospace for code, paths, commands

## File Naming
- Format: `{project} {type} description – YYYY-MM-DD.md`
- EN DASH (–) only — never em dash or hyphen
- Date ALWAYS at the end, nothing after
- Types: research, analysis, draft, rule, meeting, summary, guide, prd
- YAML frontmatter required

## Preferences
- Concise responses, no filler
- Ask before creating directories
- Edit existing files over creating new ones
```

### Professional adds:

```markdown
## Team Context
- Project: {name}
- Team: {members and roles}
- Vault: {path to shared documents}

## Communication Style
- {your rules — lowercase start, no emoji, en dash, laconic}

## Integrations
- Linear: task format (e.g., AIM-XXXX), team members
- Calendar: {Krisp MCP, gcal script, etc.}
- Messaging: {Telegram rules — forbidden channels, style}
```

### Full system adds:

```markdown
## Context Management Protocol
- Footer: `◇ ctx: {used}K | {left}K left | {pct}% | {symbol}`
- Modes: ● OK (<50%) · ◐ WARN (50-70%) · ○ CRIT (>70%)
- At CRIT: save progress, generate handoff, stop new tasks

## AI Evals Protocol
- Every response: `▫ eval: T:✓ R:✓ C:○`
- T (Text): structure, clarity, insights
- R (Rules): naming, folders, formatting
- C (Code): works, minimal, idiomatic

## Linear Awareness Layer
- Auto-detect session → task match
- Footer: `▫ linear: AIM-XXXX · title · ◐ IP`
- Suggestions: `→ /linear-action AIM-XXXX update`

## Ambient Research
- Strategic sessions: auto-launch background Exa sub-agent
- Disable: "no bg research"
```

After writing, verify:

```bash
wc -l ~/.claude/CLAUDE.md
grep "^## " ~/.claude/CLAUDE.md
```

Show: `phase 1 complete · CLAUDE.md: {lines}L · {section_count} sections`

## Phase 2: MCP Connection

**Goal**: connect data sources — at least 3 servers covering 2+ categories.

```bash
cat ~/.claude/mcp.json 2>/dev/null
```

### Recommended MCP Stack

| # | Server | Category | What It Enables | Install |
|---|--------|----------|-----------------|---------|
| 1 | **Linear** | tasks | Task tracking, /linear-action, Linear Awareness Layer | `claude mcp add linear -e LINEAR_API_KEY=lin_api_... -- npx -y @modelcontextprotocol/server-linear` |
| 2 | **filesystem** | files | Extended vault/project access | `claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem ~/Documents ~/notes` |
| 3 | **Exa** | search | /research, /ambient-advisor, fact-checking | Deferred — loads on demand via Claude Code |
| 4 | **Telegram** | messaging | Brief delivery, /intro, team comms | Custom: Telethon MTProto server |
| 5 | **Krisp** | meetings | Transcripts, action items, /daily-focus | Deferred — enable in Krisp app settings |
| 6 | **Playwright** | browser | Screenshots, visual cards, web scraping | Deferred — loads on demand |
| 7 | **context7** | docs | Library documentation lookup | Deferred — loads on demand |
| 8 | **Notion** | notes | Knowledge base, database access | `claude mcp add notion -e OPENAPI_MCP_HEADERS='...' -- npx -y @notionhq/notion-mcp-server` |
| 9 | **Netlify** | deploy | Deploy management from terminal | `claude mcp add netlify -e NETLIFY_PERSONAL_ACCESS_TOKEN=... -- npx -y @netlify/mcp` |

### MCP Categories and POS Functions

| Category | POS Function | Impact |
|----------|-------------|--------|
| **Tasks** (Linear/Jira) | Sprint awareness, status updates | Critical — feeds Linear Awareness Layer |
| **Calendar** (Krisp/gcal) | Time awareness, schedule conflicts | High — drives morning brief focus |
| **Search** (Exa/context7) | Research, fact-checking, docs | High — powers /research, /ambient-advisor |
| **Messaging** (Telegram) | Brief delivery, team comms | Medium — output beyond terminal |
| **Files** (filesystem) | Cross-project file access | Medium — extends reach of all skills |
| **Browser** (Playwright) | Visual verification, screenshots | Medium — visual card generation |
| **Notes** (Notion) | Knowledge base queries | Optional — depends on note system |
| **Deploy** (Netlify) | CI/CD from terminal | Optional — for web projects |

**Deferred servers** (Exa, Krisp, Playwright, context7) load on demand — no `claude mcp add` needed. Just ensure the service is available.

Show state and gaps:

```
  MCP SERVERS ({count})
  ├─ {name}    {category}    ✓ configured
  └─ ...

  CATEGORIES: {count}/8
  MISSING:
  · {category} — {function} — {install hint}
```

**Do NOT run install commands directly** — show for user. They need API keys.

Show: `phase 2 complete · {count} servers · {categories} categories`

## Phase 3: Skills Installation

**Goal**: install CTRL pack + user's first custom skill.

### 3.1 Install CTRL Pack

```bash
for skill in pos-audit pos-morning pos-dashboard-gen pos-skill-factory; do
  [ -f ~/.claude/skills/$skill/SKILL.md ] && echo "$skill: ✓" || echo "$skill: missing"
done
```

For missing skills:

```bash
git clone https://github.com/ai-mindset-org/pos-sprint.git /tmp/pos-sprint
bash /tmp/pos-sprint/skill-pack/install.sh
```

### 3.2 Skill Patterns (teach the user)

Skills follow 4 patterns:

| Pattern | Structure | Examples |
|---------|-----------|---------|
| **A: Audit** | scan → score → suggest | /pos-audit, vault-cleanup |
| **B: Pipeline** | detect → gather → synthesize → output | /pos-morning, daily-focus, research |
| **C: Generator** | parse input → build artifact → write | /pos-dashboard-gen, deck |
| **D: Integrator** | load MCP → payload → preview → execute | /linear-action, telegram |

Skills that use MCP ALWAYS:
1. Read `~/.claude/mcp.json` to detect servers
2. `ToolSearch: "+server_name"` to load tools
3. Call MCP functions
4. Graceful degradation: MCP unavailable → bash fallback → skip

### 3.3 First Custom Skill

After CTRL is installed, ask:

```
What's one thing you do repeatedly?

Examples from real POS setups:
· "summarize my meetings and send to telegram"
· "check my overdue tasks and nag me"
· "compress a long document to key points"
· "generate a weekly review from sessions"
```

Invoke `/pos-skill-factory` with their idea — this creates their first personal skill.

Show: `phase 3 complete · {count} skills · first custom: /{name}`

## Phase 4: Hooks Setup

**Goal**: automation triggers on session events.

### Recommended Hooks

**1. Linear Awareness (SessionStart)**

```bash
#!/bin/bash
# ~/.claude/hooks/linear-sync.sh
# Read cached Linear tasks (<200ms, no API call)
TRACKING=$(find ~/.claude/projects -name "linear-tracking.md" -type f 2>/dev/null | head -1)
[ -z "$TRACKING" ] && exit 0
IP_COUNT=$(grep -c "◐ IP" "$TRACKING" 2>/dev/null || echo 0)
TODO_COUNT=$(grep -c "○ Todo" "$TRACKING" 2>/dev/null || echo 0)
echo "--- Linear Awareness Layer ---"
echo "tasks: $IP_COUNT IP · $TODO_COUNT todo"
```

**2. Ambient Research (SessionStart)**

```bash
#!/bin/bash
# ~/.claude/hooks/ambient-advisor-start.sh
STATE="/tmp/claude-research-state.json"
[ -f "$STATE" ] && LAST=$(stat -f %m "$STATE" 2>/dev/null) || LAST=0
NOW=$(date +%s)
[ $((NOW - LAST)) -lt 600 ] && exit 0  # skip if <10min
echo "--- Ambient Advisor ---"
echo "Auto-trigger: ON. Launch background research on strategic topics."
```

**3. Open in Obsidian (PostToolUse:Write)**

```bash
#!/bin/bash
# ~/.claude/hooks/open-in-obsidian.sh
# Auto-open .md files in Obsidian after Write
FILE="$1"
VAULT_ROOT="$HOME/path/to/vault"
[[ "$FILE" == *.md ]] && [[ "$FILE" == "$VAULT_ROOT"* ]] || exit 0
REL="${FILE#$VAULT_ROOT/}"
open "obsidian://open?vault=notes&file=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$REL'))")"
```

**4. Session End Logging (SessionEnd)**

```bash
#!/bin/bash
# ~/.claude/hooks/linear-session-end.sh
# Log AIM-XXXX references from session to linear-tracking.md
```

### Setup

Ask via `AskUserQuestion` with `multiSelect: true`:

```
Which hooks? (select all that apply)

1. Linear Awareness — task context at session start (Recommended)
2. Ambient Research — auto background research on strategic topics
3. Obsidian Integration — auto-open written .md files
4. Session Logging — log Linear task references at session end
```

For each: create script in `~/.claude/hooks/`, add to hooks config, verify.

**Most users: start with just Linear Awareness** — lowest friction, highest value.

Show: `phase 4 complete · {count} hooks active`

## Phase 5: Operational Layer

**Goal**: activate daily systems — morning brief, settings, quality eval.

### 5.1 Morning Brief Demo

Run `/pos-morning` — the **"aha moment"**. All data sources synthesized into one focus sentence.

The brief auto-detects MCP servers and degrades gracefully:
- Calendar: Krisp MCP → gcal script → skip
- Tasks: Linear MCP → cache → local TODO → skip
- Messages: Telegram saved → skip
- Sessions: recent JSONL scan

### 5.2 Settings

```bash
cat ~/.claude/settings.json 2>/dev/null
```

Recommend:

| Setting | Value | Why |
|---------|-------|-----|
| `defaultMode` | `"dontAsk"` | Full autonomy for trusted tools |
| `statusLine` | `"~/.claude/statusline.sh"` | Custom project-aware statusline |

### 5.3 Auto Memory

Verify memory is working:

```bash
find ~/.claude/projects -name "MEMORY.md" -type f 2>/dev/null
```

Memory activates after a few sessions. It accumulates patterns and project context.

### 5.4 Eval Protocol (score 8+)

For advanced users, add self-evaluation to every response:

```
▫ eval: T:✓ R:✓ C:○
```

T (Text quality), R (Rules compliance), C (Code quality). Binary pass/fail.

Show: `phase 5 complete · morning: tested · settings: ✓ · memory: {status}`

## Phase 6: Dashboard Generation

Run `/pos-dashboard-gen` for a visual snapshot:

```
  generating dashboard...
  ├─ gathering: calendar, tasks, sessions, skills, docs
  ├─ building: terminal aesthetic, responsive grid
  └─ writing: /tmp/pos-dashboard.html

  → open /tmp/pos-dashboard.html
```

Show: `phase 6 complete · dashboard at /tmp/pos-dashboard.html`

## Final Output

```
┌─────────────────────────────────────────────────────┐
│  POS SETUP COMPLETE · {date}                         │
└─────────────────────────────────────────────────────┘

  INFRASTRUCTURE
  ├─ context      ~/.claude/CLAUDE.md     {lines}L
  ├─ mcp          {count} servers         {categories}
  ├─ skills       {count} installed       +{custom} custom
  ├─ hooks        {count} active          {types}
  ├─ operations   memory: ✓  morning: ✓   eval: {on|off}
  └─ dashboard    /tmp/pos-dashboard.html

  POS SCORE: {score}/12
  ──────────────────────────────────────────────────

  DAILY WORKFLOW:
  1. /pos-morning      → focus sentence for the day
  2. work on tasks     → Linear Awareness tracks context
  3. /pos-audit        → weekly health check
  4. /pos-skill-factory → when you spot a repeating workflow

  RESOURCES:
  · skill pack:  github.com/ai-mindset-org/pos-sprint/tree/main/skill-pack
  · dashboard:   ai-mindset-org.github.io/pos-sprint/
  · community:   submit skills via PR to pos-sprint repo
```

## Principles

- **Auto-detect and skip**: never repeat completed work
- **Show, don't just tell**: each phase produces a visible artifact
- **User controls execution**: show MCP commands, don't run them
- **"Aha moment"**: Phase 5 morning brief is the turning point
- **Graceful partial runs**: any subset of phases is useful
- **Real patterns**: every recommendation comes from tested practice

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running all phases when setup exists | Always detect state first, skip completed |
| Installing MCP without asking | Show commands, user runs — they need API keys |
| Skipping first custom skill | This is the "aha moment" — POS becomes theirs |
| Generic CLAUDE.md | Ask about user's actual work, team, workflows |
| Not testing /pos-morning | The morning brief demo makes POS click |
| Treating hooks as required for beginners | Start with 0-1 hooks, add after a week |
| Hardcoded paths | Always use `~` or `$HOME` |
