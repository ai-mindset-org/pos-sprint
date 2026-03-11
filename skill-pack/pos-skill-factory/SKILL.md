---
name: pos-skill-factory
description: Create a new Claude Code skill from a description. Generates SKILL.md, suggests location, and installs it.
version: 1.0
user_invocable: true
arguments:
  - name: idea
    description: "What the skill should do (natural language)"
    required: true
---

# POS Skill Factory — Build Skills from Ideas

Create a new Claude Code skill from a natural language description. Generates proper SKILL.md, suggests install location, and installs it.

## Process

### Step 1: Understand the Idea

Parse the user's `{idea}` and determine:

1. **What it does** — core action (generate, analyze, send, create, search, transform)
2. **What it needs** — inputs (files, API data, user input, context)
3. **What it outputs** — result format (text, file, message, HTML)
4. **What tools it uses** — MCP servers, Bash, Read/Write, external APIs

### Step 2: Generate Skill Name

Rules:
- Lowercase, hyphenated: `morning-brief`, `weekly-review`, `task-sorter`
- 2-3 words max
- Verb-noun pattern preferred: `check-tasks`, `send-digest`, `generate-report`
- No prefix needed (user can add project prefix later)

### Step 3: Generate SKILL.md

Follow this structure exactly:

```markdown
---
name: {skill-name}
description: {one-line description — what it does, when to use it}
version: 1.0
user_invocable: true
arguments:          # only if skill takes parameters
  - name: {param}
    description: "{what it controls}"
    required: false
---

# {Skill Name} — {Subtitle}

{2-3 sentences: what this skill does and why.}

## How it works

{Step-by-step instructions for Claude Code to follow when this skill is invoked.
Be specific about:
- What to read/fetch
- How to process
- What format to output}

## Output Format

{Show exact format with monospace blocks. Use box-drawing characters for structure:
┌─ ├─ └─ for trees, ─── for dividers}

## Principles

- {Key behavior rule}
- {Error handling approach}
- {What to skip if unavailable}
```

### Step 4: Ask Where to Install

Present options:

```
Where to install {skill-name}?

1. Global (~/.claude/skills/{skill-name}/SKILL.md)
   → available in all projects

2. Project (.claude/skills/{skill-name}/SKILL.md)
   → only in current project

3. Just show me the file (don't install)
```

### Step 5: Install

Create the directory and SKILL.md file at the chosen location.

Verify installation:
```bash
ls -la {install-path}/SKILL.md
```

### Step 6: Test Suggestion

After installation, suggest:

```
Skill installed! Test it:

  /{skill-name}

To edit later:
  {install-path}/SKILL.md
```

## Quality Rules for Generated Skills

1. **Self-contained**: Skill must work without external dependencies it can't check for
2. **Graceful degradation**: If a data source is missing, skip it — don't error
3. **Specific output format**: Always include exact output format, not vague descriptions
4. **Monospace-first**: Use box-drawing characters (┌├└─│) for structure
5. **No boilerplate**: Don't add sections the skill doesn't need
6. **Tool-aware**: Specify which Claude Code tools to use (Read, Write, Bash, Grep, Glob, MCP)
7. **Concise**: SKILL.md should be 40-100 lines. Longer = too complex, split into multiple skills

## Examples

### Input: "send me a summary of what I did today to telegram"
→ Skill: `daily-recap` — reads today's sessions, generates compact summary, sends to Saved Messages via Telegram MCP

### Input: "check my overdue tasks and nag me"
→ Skill: `task-nag` — reads Linear tasks, filters overdue, formats urgent list with suggested actions

### Input: "generate a weekly review from my sessions"
→ Skill: `weekly-review` — reads week's JSONL logs, extracts topics/tools, generates activity report

### Input: "create a cheat sheet from a document"
→ Skill: `cheat-sheet` — reads target file, extracts key concepts, formats as dense 1-page reference
