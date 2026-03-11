---
name: pos-skill-factory
description: Create a new Claude Code skill from a description. 4 template patterns, quality validation, install to chosen location.
version: 3.0
user_invocable: true
arguments:
  - name: idea
    description: "What the skill should do (natural language)"
    required: true
---

# POS Skill Factory — Build Skills from Ideas

Create a production-quality Claude Code skill from a natural language description. Uses 4 template patterns from real POS implementations, validates against a quality checklist, and installs to the right location.

## Step 1: Understand the Idea

Parse `{idea}` and determine:

1. **Core action** — scan, generate, send, transform, aggregate, analyze, summarize
2. **Inputs** — files, MCP data, user input, context, CLI args
3. **Outputs** — terminal text, file, message, HTML, structured data
4. **Tools needed** — Read/Write, Bash, Grep, Glob, MCP, ToolSearch, Task (sub-agents)
5. **Pattern** — which of the 4 templates fits best

## Step 2: Select Template Pattern

### Pattern A: Audit (scan + score + suggest)

**When**: skill examines a system, counts things, produces a score.
**Structure**: discover sources → scan each → aggregate → score → suggest gaps.
**Real examples**: `/pos-audit` (POS infrastructure), `vault-cleanup` (Obsidian maintenance), `security-scan` (secrets/permissions).

```
## Step 0: Discover sources
  {read mcp.json, find files, check configs}
## Step 1-N: Scan each source
  {extract data, categorize, count}
## Output: scored report
  {box-drawing table with score breakdown}
## Scoring table
  {component | points | criteria}
## Gap suggestions
  {score range → recommended action}
```

### Pattern B: Pipeline (gather + synthesize + output)

**When**: skill pulls from multiple sources and synthesizes a result.
**Structure**: detect integrations → gather from each (with degradation) → synthesize → output in chosen format.
**Real examples**: `/pos-morning` (daily brief), `/daily-focus` (5 parallel agents → brief + visual card), `/research` (multi-angle Exa search → synthesis).

```
## Step 0: Detect integrations
  {read mcp.json, build source map}
## Step 1: Gather from each source
  {degradation chain: MCP → bash fallback → skip}
## Step 2: Synthesize
  {derive insight from combined data}
## Step 3: Output
  {multiple format options: terminal, file, message}
```

**Key Pipeline pattern**: always start with MCP detection and use **graceful degradation chains**:
```
Calendar: Krisp MCP → gcal script → skip
Tasks: Linear MCP → cache file → local TODO → skip
Messages: Telegram MCP → skip
```

### Pattern C: Generator (input + transform + write)

**When**: skill takes input and produces a file or artifact.
**Structure**: parse input → apply template/rules → write output → verify.
**Real examples**: `/pos-dashboard-gen` (HTML dashboard), `/deck` (HTML presentations), `/imagine` (image generation via API).

```
## Step 1: Parse input
  {args or interactive questions}
## Step 2: Build artifact
  {HTML, markdown, image, etc.}
## Step 3: Write and verify
  {write file, check size, open in browser/app}
## Design system (if visual)
  {CSS variables, fonts, color scheme}
```

### Pattern D: Integrator (detect + connect + execute)

**When**: skill wraps an external service with opinionated defaults.
**Structure**: ToolSearch → build payload → show preview → confirm → execute → report.
**Real examples**: `/linear-action` (Linear CRUD with pre-fill), `/telegram` (MTProto messaging), `/calendar` (gcal with fallback chain).

```
## Step 0: Load MCP tools
  {ToolSearch: "+server_name"}
## Step 1: Build payload
  {pre-fill from context — session topic, recent work}
## Step 2: Preview → confirm
  {show what will happen, ask y/edit/skip}
## Step 3: Execute and report
  {MCP call, format result}
```

**Key Integrator pattern**: always **pre-fill then confirm**:
```
AIM-2054 · Sprint review prep · ◐ IP
action: update
comment: "completed slide deck, ready for review"
→ execute? [y/edit/skip]
```

## Step 3: Generate Skill Name

Rules:
- **Lowercase, hyphenated**: `morning-brief`, `weekly-review`, `task-sorter`
- **2-3 words max**: never more than 3
- **Verb-noun preferred**: `check-tasks`, `send-digest`, `scan-vault`
- **No generic verbs**: avoid `do-`, `run-`, `make-` — be specific
- **No project prefix**: user adds their own prefix (e.g., `aim-`)

**Validation**: name must complete "I want to _____" naturally.
- Good: "I want to `check-tasks`"
- Bad: "I want to `task-thing`"

## Step 4: Generate SKILL.md

Follow Claude Code skill spec exactly:

```markdown
---
name: {skill-name}
description: {ONE line — what it does. Must fit in a skill listing.}
version: 1.0
user_invocable: true
arguments:          # only if skill takes parameters
  - name: {param}
    description: "{what it controls}"
    required: false
---

# {Title} — {Subtitle}

{2-3 sentences: what, why, when.}

## Step 0: {Detect/Discover} (if MCP-dependent)

{Read ~/.claude/mcp.json, ToolSearch for servers}

## Step N: {Action}

{Specific instructions with:
- Exact tool calls (Read, Write, Bash, Grep, Glob, ToolSearch)
- MCP function names
- Degradation chains (try A → try B → skip)
- What to do with the data}

## Output Format

{EXACT format with box-drawing characters:
┌─ ├─ └─ for trees
─── for dividers}

## Principles

- {Key behavior rule}
- {Graceful degradation}
- {What to never do}

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| {wrong approach} | {correct approach} |
```

### Spec Rules

- **YAML frontmatter**: `name`, `description` (one line), `version`, `user_invocable: true`
- **description**: one line that fits a skill listing — not a paragraph
- **arguments**: only if behavior genuinely changes with parameters
- **Box-drawing**: `┌ ├ └ ─ │` for all structured output
- **Paths**: `~` or `$HOME`, never hardcoded personal paths
- **Common Mistakes**: ALWAYS include, 3-6 rows minimum
- **MCP pattern**: Step 0 reads mcp.json → ToolSearch → degradation chain

## Step 5: Preview and Location

Show the skill, then ask via `AskUserQuestion`:

```
Generated: /{skill-name}
Pattern: {A|B|C|D} — {name}
Lines: {count}
Sections: {list of ## headers}

Where to install?

1. Global (~/.claude/skills/) — available everywhere (Recommended)
2. Project (.claude/skills/) — only current directory
3. Show only — don't install yet
```

## Step 6: Install and Verify

```bash
mkdir -p {path}/{skill-name}
```

Write SKILL.md with the Write tool (not bash).

Verify:

```bash
wc -l {path}/{skill-name}/SKILL.md
```

## Step 7: Post-Install

```
/{skill-name} installed

  path: {full_path}/SKILL.md
  size: {lines} lines
  pattern: {A|B|C|D} — {name}

  test:  /{skill-name}
  edit:  {full_path}/SKILL.md
```

## Quality Checklist

Validate all 7 before writing:

| # | Check | Criteria |
|---|-------|----------|
| 1 | **Self-contained** | Works without deps it can't detect |
| 2 | **Graceful degradation** | Missing source = skip, not error |
| 3 | **Specific output** | Exact format shown, not "generate report" |
| 4 | **Monospace-first** | Box-drawing chars for all structure |
| 5 | **Tool-aware** | Names which Claude Code tools to use |
| 6 | **Right size** | 40-150 lines. Longer → split into skills |
| 7 | **Anonymized** | `~` or `$HOME`, no personal paths |

Fix before preview if any check fails.

## Real Examples

| User says | Skill | Pattern | Key feature |
|-----------|-------|---------|-------------|
| "summarize meetings and send to TG" | `meeting-digest` | B Pipeline | Krisp → synthesize → telegram send |
| "nag me about overdue tasks" | `task-nag` | D Integrator | Linear → filter overdue → urgent list |
| "weekly review from sessions" | `weekly-review` | B Pipeline | JSONL scan → topic extraction → report |
| "audit my security" | `security-scan` | A Audit | .env, secrets, permissions → scored |
| "HTML from markdown" | `md-to-html` | C Generator | Read .md → template → write .html |
| "check vault health" | `vault-health` | A Audit | File count, size, orphans → scored |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Description > 1 line | One sentence max — must fit skill listing |
| Args skill doesn't need | Only add if behavior genuinely changes |
| Vague output: "nice report" | Show EXACT format with box-drawing |
| No MCP degradation chain | Always: MCP → file fallback → skip |
| Skill > 150 lines | Split into 2 — a skill does ONE thing |
| Missing Common Mistakes | Every skill needs 3-6 rows minimum |
| Not checking mcp.json first | Step 0 discovers what's available |
