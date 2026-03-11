---
name: pos-setup
description: Build your Personal Operating System from zero — 6-phase pipeline with auto-detection. Context, MCP, skills, operations, dashboard.
version: 1.0
user_invocable: true
arguments:
  - name: phase
    description: "Run specific phase: audit, context, mcp, skills, ops, dashboard (default: auto-detect)"
    required: false
---

# POS Setup — Build Your Personal Operating System

Sequential pipeline that takes you from zero to a working Personal Operating System. Auto-detects current state, skips completed phases, guides through each layer. Run once to build, run again to verify and extend.

## Step 0: Quick State Detection

Before starting any phase, run a lightweight check to determine what already exists:

```bash
# Check each layer
CLAUDE_GLOBAL=$([ -f ~/.claude/CLAUDE.md ] && wc -l < ~/.claude/CLAUDE.md || echo 0)
CLAUDE_PROJECT=$([ -f .claude/../CLAUDE.md ] && echo "yes" || echo "no")
SKILLS_COUNT=$(ls ~/.claude/skills/*/SKILL.md ~/.claude/skills/*.md 2>/dev/null | wc -l)
MCP_SERVERS=$(cat ~/.claude/mcp.json 2>/dev/null | grep -c '"command"' || echo 0)
HOOKS_SET=$([ -f ~/.claude/hooks.json ] && echo "yes" || echo "no")
MEMORY_FILES=$(find ~/.claude/projects -name "MEMORY.md" 2>/dev/null | wc -l)
```

Build a state map and show it:

```
  POS STATE CHECK
  ├─ context      {CLAUDE_GLOBAL}L global · project: {yes|no}
  ├─ mcp          {MCP_SERVERS} servers
  ├─ skills       {SKILLS_COUNT} installed
  ├─ operations   hooks: {yes|no} · memory: {MEMORY_FILES} projects
  └─ dashboard    {exists|missing}

  starting from phase: {first incomplete phase}
```

If `{phase}` argument is provided, jump directly to that phase. Otherwise, start from the first phase that scores below threshold.

**Phase thresholds** (skip if met):
- context: global CLAUDE.md > 20 lines
- mcp: 3+ servers across 2+ categories
- skills: 3+ skills installed
- ops: hooks configured OR memory active
- dashboard: `/tmp/pos-dashboard.html` exists and < 24h old

## Phase 1: Context Assembly

**Goal**: create `~/.claude/CLAUDE.md` — your persistent identity layer.

**If CLAUDE.md exists and > 20 lines**: show current sections, ask if user wants to extend. Skip if user says no.

**If missing or < 20 lines**: guide through creation.

Ask user with `AskUserQuestion`:

```
What should your POS know about you?

1. Quick start — minimal rules (naming, format, tools)
2. Professional — work context, team, communication style
3. Full setup — identity, values, workflows, integrations
```

### Quick start template (write with Write tool):

```markdown
# Claude Code Rules

## Formatting
- Use **bold** for key concepts
- Markdown structure with clear headers
- Monospace for code, paths, commands

## File Naming
- Format: `{project} {type} description – YYYY-MM-DD.md`
- Lowercase types: research, analysis, draft, rule, meeting

## Preferences
- Concise responses, no filler
- Ask before creating new directories
- Prefer editing existing files over creating new ones
```

### Professional template adds:
- Team/project context section
- Communication style rules
- Tool preferences (IDE, terminal, language)
- Integration references

### Full setup template adds:
- Values and principles
- Workflow definitions (morning routine, review cadence)
- Context management protocol
- Cross-project coordination rules

After writing, verify:

```bash
wc -l ~/.claude/CLAUDE.md
```

Show: `phase 1 complete · CLAUDE.md: {lines}L`

## Phase 2: MCP Connection

**Goal**: connect minimum viable stack — at least 3 MCP servers covering 2+ categories.

**Minimum viable stack** (recommended order):

| Priority | Category | Server | Install Command |
|----------|----------|--------|----------------|
| 1 | Files | filesystem | `claude mcp add filesystem -- npx -y @anthropic-ai/mcp-filesystem` |
| 2 | Tasks | linear | `claude mcp add linear -e LINEAR_API_KEY=your_key -- npx -y @anthropic-ai/mcp-linear` |
| 3 | Search | context7 | `claude mcp add context7 -- npx -y @anthropic-ai/mcp-context7` |
| 4 | Calendar | krisp | Check if Krisp app installed, enable MCP in settings |
| 5 | Messaging | telegram | Custom setup — see telegram-mcp docs |
| 6 | Browser | playwright | `claude mcp add playwright -- npx -y @anthropic-ai/mcp-playwright` |

**Detection**: read `~/.claude/mcp.json`, categorize existing servers.

Show current state:

```
  MCP SERVERS ({count})
  ├─ {name}    {category}    ✓ configured
  └─ ...

  MISSING CATEGORIES:
  · {category} — {why it matters} — {install command}
```

Ask user which servers to add (show install commands). For each selection:
1. Show the exact `claude mcp add` command
2. Note if API key is needed
3. After user runs command, verify by reading updated `~/.claude/mcp.json`

**Do NOT run `claude mcp add` commands directly** — they modify global config. Show commands for user to run.

Show: `phase 2 complete · {count} servers · {categories} categories`

## Phase 3: Skills Installation

**Goal**: install foundational skill pack + user's first custom skill.

### 3.1 Install CTRL Pack

Check which CTRL skills are already installed:

```bash
for skill in pos-audit pos-morning pos-dashboard-gen pos-skill-factory; do
  [ -f ~/.claude/skills/$skill/SKILL.md ] && echo "$skill: installed" || echo "$skill: missing"
done
```

For missing skills, offer to install from GitHub:

```bash
# Show command for user
git clone https://github.com/ai-mindset-org/pos-sprint.git /tmp/pos-sprint
bash /tmp/pos-sprint/skill-pack/install.sh
```

### 3.2 First Custom Skill

After CTRL pack is installed, ask:

```
What's one thing you do repeatedly that Claude Code could automate?

Examples:
· "summarize my meetings"
· "check my overdue tasks"
· "send daily update to team chat"
· "review my PR changes"
```

Take the user's answer and invoke `/pos-skill-factory` with their idea. This creates their first personal skill — the "aha moment" of POS.

Show: `phase 3 complete · {count} skills installed · first custom: /{skill-name}`

## Phase 4: Daily Operations

**Goal**: configure the operational layer — hooks, auto-memory, morning routine.

### 4.1 Auto Memory

Auto memory is enabled by default in Claude Code. Verify it's working:

```bash
find ~/.claude/projects -name "MEMORY.md" -type f 2>/dev/null | head -5
```

If no memory files exist, explain: "Auto memory activates after a few sessions. Claude Code will start noting patterns, decisions, and project context automatically."

### 4.2 Morning Brief Test

Run `/pos-morning` to demonstrate the daily brief pipeline. This is the "aha moment" — seeing all your data sources synthesized into one focused brief.

If pos-morning is not installed, install it first (Phase 3).

### 4.3 Hooks (optional)

For users at score 7+, suggest hooks:

```
  SUGGESTED HOOKS:
  · SessionStart — run /pos-morning automatically
  · PreToolUse:Write — lint check before file creation
  · PostToolUse:Bash — capture command history

  Hooks require editing ~/.claude/hooks.json
  Skip for now? Most users add hooks after 1-2 weeks of use.
```

Show: `phase 4 complete · memory: {status} · morning: tested · hooks: {count|skipped}`

## Phase 5: Dashboard Generation

**Goal**: generate a personal HTML dashboard as a visual snapshot.

Run `/pos-dashboard-gen` to create the dashboard. This pulls from all configured sources and builds a single-file HTML page.

```
  generating dashboard...
  ├─ gathering: calendar, tasks, sessions, skills, docs
  ├─ building: terminal aesthetic, responsive grid
  └─ writing: /tmp/pos-dashboard.html

  → open /tmp/pos-dashboard.html
```

Show: `phase 5 complete · dashboard at /tmp/pos-dashboard.html`

## Final Output

After all phases (or after the last completed phase):

```
┌─────────────────────────────────────────────────────┐
│  POS SETUP COMPLETE · {date}                         │
└─────────────────────────────────────────────────────┘

  INFRASTRUCTURE
  ├─ context      ~/.claude/CLAUDE.md     {lines}L
  ├─ mcp          {count} servers         {categories}
  ├─ skills       {count} installed       +{custom} custom
  ├─ operations   memory: ✓  hooks: {n}   morning: ✓
  └─ dashboard    /tmp/pos-dashboard.html

  POS SCORE: {score}/12
  ──────────────────────────────────────────────────

  NEXT STEPS:
  · run /pos-morning every day — it gets better with context
  · run /pos-audit weekly — track your POS growth
  · run /pos-skill-factory when you spot a repeating workflow
  · run /pos-dashboard-gen to refresh your snapshot

  RESOURCES:
  · dashboard:  https://ai-mindset-org.github.io/pos-sprint/
  · skill pack: https://github.com/ai-mindset-org/pos-sprint/tree/main/skill-pack
  · community:  submit your skills via PR to pos-sprint repo
```

## Principles

- **Auto-detect and skip**: never repeat completed work — check state first
- **Show, don't just tell**: each phase produces a visible artifact
- **User controls execution**: show MCP install commands, don't run them directly
- **The "aha moment"**: Phase 4 morning brief is the turning point — prioritize getting there
- **Graceful partial runs**: any subset of phases is useful — don't require all 5
- **No hardcoded paths**: use `~` and `$HOME` everywhere

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running all phases even when setup exists | Always detect state first, skip completed phases |
| Installing MCP servers without asking | Show commands, let user run them — they need API keys |
| Skipping the "first custom skill" step | This is the aha moment — the user sees POS is THEIRS to extend |
| Generic CLAUDE.md template | Ask about user's actual work, team, and preferences |
| Not testing /pos-morning during setup | The morning brief demo is what makes POS click |
| Treating dashboard as required | Dashboard is optional — a working morning brief is more valuable |
