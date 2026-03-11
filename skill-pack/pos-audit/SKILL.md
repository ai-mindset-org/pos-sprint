---
name: pos-audit
description: Scan your POS infrastructure — CLAUDE.md, skills, MCP servers, memory, hooks, settings. Score 0-12 with gap analysis.
version: 3.0
user_invocable: true
---

# POS Audit — Infrastructure Scanner

Scan your entire Claude Code setup, cross-reference components, and produce a scored assessment with actionable gaps. Based on 6 diagnostic layers matching the POS setup pipeline.

## Step 0: Discover MCP Servers

Read MCP configuration BEFORE scanning anything else — the server list drives capability detection.

```bash
cat ~/.claude/mcp.json 2>/dev/null
cat .claude/mcp.json 2>/dev/null
```

Parse JSON and categorize each server:

| Category | Server Examples | POS Function |
|----------|----------------|--------------|
| Tasks | linear, jira | Sprint awareness, status tracking |
| Calendar | krisp, google-calendar | Time awareness, meeting prep |
| Search | exa, context7 | Research, documentation, fact-checking |
| Messaging | telegram, slack | Brief delivery, team communication |
| Files | filesystem | Cross-project file access |
| Browser | playwright, browsermcp | Screenshots, web interaction |
| Notes | notion, obsidian | Knowledge base queries |
| Deploy | netlify, vercel | CI/CD management |

**Capability score**: count CATEGORIES covered, not server count. 5 filesystem mounts = 1 category.

Also check for deferred/marketplace servers by scanning skill files for ToolSearch patterns:

```bash
grep -r "ToolSearch\|mcp__" ~/.claude/skills/*/SKILL.md 2>/dev/null | grep -o 'mcp__[a-z_]*' | sort -u
```

This reveals servers used in skills but not in mcp.json (deferred servers loaded on-demand).

## Step 1: CLAUDE.md Analysis (Context Layer)

```bash
cat ~/.claude/CLAUDE.md 2>/dev/null | wc -l
find . -name "CLAUDE.md" -maxdepth 2 2>/dev/null
find . -name "AGENTS.md" -maxdepth 2 2>/dev/null
```

**Parse and report sections** — don't just count lines:

| Section | What to look for | Quality signal |
|---------|-----------------|----------------|
| Formatting | Bold rules, markdown standards | Has specific rules, not "be clear" |
| Naming | `{project} {type} description – date` convention | EN dash, date at end, project codes |
| Integrations | MCP references, service names | References match installed servers |
| Workflows | Pipelines, morning routine, review cadence | Operational, not aspirational |
| Context mgmt | Handoff protocol, footer format | Threshold-based, symbols defined |
| Eval protocol | T/R/C binary assessment | Rubric exists, footer format defined |
| Linear awareness | Task detection, footer display | Action suggestions, URL patterns |

**Cross-reference**: check if tools/skills mentioned in CLAUDE.md actually exist.

```bash
# Extract skill names mentioned in CLAUDE.md
grep -o '/[a-z-]*' ~/.claude/CLAUDE.md 2>/dev/null | sort -u
```

Compare against installed skills — flag ghosts (mentioned but missing) and orphans (installed but never referenced).

## Step 2: Skills Inventory

```bash
# Global skills
ls ~/.claude/skills/*/SKILL.md 2>/dev/null
ls ~/.claude/skills/*.md 2>/dev/null

# Project skills
ls .claude/skills/*/SKILL.md 2>/dev/null
```

For each skill:
- Read first 5 lines for `name:` and `description:` from YAML frontmatter
- Categorize: `infrastructure` | `workflow` | `integration` | `content` | `creative` | `utility`
- Flag skills without proper YAML frontmatter (not production-ready)

### Skill Pattern Detection

Count skills by pattern:

| Pattern | Signal | Examples |
|---------|--------|---------|
| A: Audit | scans, scores, reports | pos-audit, vault-cleanup |
| B: Pipeline | gathers from sources, synthesizes | pos-morning, research, daily-focus |
| C: Generator | produces files/artifacts | pos-dashboard-gen, deck, imagine |
| D: Integrator | wraps MCP with opinionated defaults | linear-action, telegram, calendar |

A healthy POS has skills in at least 3 of 4 patterns.

## Step 3: MCP Capability Matrix

Using servers from Step 0, test each:

```
ToolSearch: "+{server_name}"
```

Report status:

```
  MCP CAPABILITY MATRIX
  ├─ linear             tasks          ✓ loaded
  ├─ krisp              meetings       ✓ loaded
  ├─ telegram           messaging      ✓ loaded
  ├─ exa                search         ✓ loaded (deferred)
  ├─ filesystem         files          ✓ loaded
  ├─ playwright         browser        ✓ loaded (deferred)
  └─ context7           docs           ✓ loaded (deferred)
```

Statuses: `✓ loaded` | `✗ config only` (in mcp.json but not responding) | `◌ deferred` (used in skills, not in mcp.json)

## Step 4: Memory & Persistence

```bash
# Auto memory files
find ~/.claude/projects -name "MEMORY.md" 2>/dev/null

# Memory file count and size
find ~/.claude/projects -path "*/memory/*" -type f 2>/dev/null | wc -l
du -sh ~/.claude/projects/*/memory/ 2>/dev/null

# Episodic memory plugin
find ~/.claude -path "*episodic*" -type d 2>/dev/null
```

Report: project count with memory, total files, total size, most recently updated.

**Quality check**: read MEMORY.md content — is it useful or just boilerplate? Look for:
- Named conventions or patterns
- Project-specific decisions
- Cross-session state (e.g., Linear task caches)

## Step 5: Hooks & Automation

```bash
cat ~/.claude/hooks.json 2>/dev/null
cat ~/.claude/settings.json 2>/dev/null | grep -A5 '"hooks"'
ls ~/.claude/hooks/ 2>/dev/null
```

For each hook, report:
- **Trigger**: `SessionStart` | `SessionEnd` | `PostToolUse:Write` | `PreToolUse` | etc.
- **Script**: what it does (read the script file)
- **Impact**: what POS capability it enables

### Known Hook Patterns

| Hook | Trigger | POS Capability |
|------|---------|---------------|
| Linear sync | SessionStart | Linear Awareness Layer in footer |
| Ambient advisor | SessionStart | Background research auto-trigger |
| Open in Obsidian | PostToolUse:Write | Auto-open .md in Obsidian |
| Session logging | SessionEnd | Linear task reference tracking |
| Daily sessions | SessionEnd | Session history capture |

## Step 6: Settings & Permissions

```bash
cat ~/.claude/settings.json 2>/dev/null
```

Report:
- **Permission mode**: `default` | `dontAsk` | `plan` | `bypassPermissions`
- **Allowed tools**: explicit allow patterns
- **Plugins**: installed plugin list with versions
- **StatusLine**: custom or default
- **Additional directories**: extra paths in context

## Output Format

```
┌─────────────────────────────────────────────────────┐
│  POS AUDIT · {date}                                  │
│  dir: {cwd}                                          │
│  mcp: {count} servers · {categories} categories      │
└─────────────────────────────────────────────────────┘

  CONTEXT                                         {✓|✗}
  ├─ CLAUDE.md (global)     {lines}L  {sections}
  ├─ CLAUDE.md (project)    {lines}L  {sections}
  ├─ AGENTS.md              {status}
  └─ cross-ref              {matched}/{total} skills

  SKILLS                                          {count}
  ├─ infrastructure  {list}
  ├─ workflow         {list}
  ├─ integration      {list}
  ├─ content          {list}
  ├─ ghosts           {mentioned but not installed}
  └─ orphans          {installed but not referenced}

  MCP SERVERS                                     {count}
  ├─ {name}  {category}  {status}
  └─ coverage: {categories}/{8}

  MEMORY                                          {files}
  ├─ projects    {count} with memory
  ├─ total       {size}
  └─ episodic    {installed|not found}

  HOOKS                                           {count}
  └─ {trigger}: {description}

  SETTINGS
  ├─ permissions   {mode}
  ├─ plugins       {count} ({names})
  └─ statusline    {custom|default}

  ─────────────────────────────────────────────────

  POS SCORE: {score}/12

  ┌─ Breakdown ─────────────────────────────────┐
  │ CLAUDE.md exists        {0-1}/{1}   {note}  │
  │ CLAUDE.md quality       {0-1}/{1}   {note}  │
  │ Skills > 0              {0-1}/{1}   {note}  │
  │ Skills > 5              {0-1}/{1}   {note}  │
  │ MCP > 0                 {0-1}/{1}   {note}  │
  │ MCP diversity           {0-1}/{1}   {note}  │
  │ Memory active           {0-1}/{1}   {note}  │
  │ Hooks configured        {0-1}/{1}   {note}  │
  │ AGENTS.md               {0-1}/{1}   {note}  │
  │ Project CLAUDE.md       {0-1}/{1}   {note}  │
  │ Cross-referencing       {0-1}/{1}   {note}  │
  │ Settings configured     {0-1}/{1}   {note}  │
  └─────────────────────────────────────────────┘

  GAPS (highest impact first):
  1. {gap + specific action}
  2. {gap + specific action}
  3. {gap + specific action}
```

## Scoring (12 points)

| Component | Points | Criteria |
|-----------|--------|----------|
| CLAUDE.md exists | 1 | Any CLAUDE.md (global or project) |
| CLAUDE.md quality | 1 | >50 lines with named sections (naming, integrations, workflows) |
| Skills > 0 | 1 | Has any installed skills |
| Skills > 5 | 1 | Meaningful skill library with 3+ patterns |
| MCP > 0 | 1 | Has any MCP servers configured |
| MCP diversity | 1 | 3+ categories covered |
| Memory active | 1 | Auto memory exists with content (not empty) |
| Hooks configured | 1 | Any hooks set up |
| AGENTS.md | 1 | Project has agent index |
| Project CLAUDE.md | 1 | Project-specific rules (not just global) |
| Cross-referencing | 1 | >80% of skills mentioned in CLAUDE.md exist |
| Settings configured | 1 | Non-default permissions or custom statusline |

## Gap Suggestions

| Score | Focus |
|-------|-------|
| 0-3 | "Start: `~/.claude/CLAUDE.md` + 1 skill + 1 MCP server → run /pos-setup" |
| 4-6 | "Grow: more skills, MCP diversity, enable auto memory" |
| 7-9 | "Automate: hooks, Linear awareness, morning brief pipeline" |
| 10-12 | "Share: dashboard, skill packs, community contributions" |

Always suggest the **single highest-impact action** as gap #1.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Counting servers instead of categories | 5 filesystem mounts = 1 category |
| Skipping cross-reference check | Ghost skills waste CLAUDE.md context tokens |
| Not reading SKILL.md frontmatter | Name/description tells if skill is real or placeholder |
| Reporting empty memory dirs as active | Check content, not just file existence |
| Missing deferred servers | Scan skill files for `mcp__` patterns, not just mcp.json |
| Hardcoded paths in report | Use `~` or `$HOME` in all suggestions |
