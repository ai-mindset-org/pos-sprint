---
name: pos-audit
description: Audit your POS — list all components (CLAUDE.md, skills, MCP servers, memory, hooks). Shows what you have and what's missing.
version: 1.0
user_invocable: true
---

# POS Audit — Personal OS Inventory

Scan your Claude Code setup and report what POS components you have, their state, and gaps.

## What to scan

### 1. CLAUDE.md Files (Constitution)

```bash
# Global rules
cat ~/.claude/CLAUDE.md 2>/dev/null | wc -l

# Project-level rules
find . -name "CLAUDE.md" -maxdepth 2 2>/dev/null

# AGENTS.md
find . -name "AGENTS.md" -maxdepth 2 2>/dev/null
```

Report: exists/missing, line count, key sections found.

### 2. Skills

```bash
# Global skills
ls ~/.claude/skills/*/SKILL.md 2>/dev/null
ls ~/.claude/skills/*.md 2>/dev/null

# Project skills
ls .claude/skills/*/SKILL.md 2>/dev/null
ls .claude/skills/*.md 2>/dev/null
```

Report: count, list with names, categorize by type (utility, content, workflow, integration).

### 3. MCP Servers

```bash
# Global MCP config
cat ~/.claude/mcp.json 2>/dev/null

# Project MCP config
cat .claude/mcp.json 2>/dev/null
```

Report: list of configured servers, their types (filesystem, API, custom).

### 4. Memory Files

```bash
# Auto memory
ls ~/.claude/projects/*/memory/ 2>/dev/null

# Episodic memory
ls ~/.claude/projects/*/episodic-memory/ 2>/dev/null 2>&1 | head -5
```

Report: memory file count, total size, last updated.

### 5. Hooks

```bash
cat ~/.claude/hooks.json 2>/dev/null
cat .claude/hooks.json 2>/dev/null
```

Report: active hooks, their triggers.

### 6. Settings

```bash
cat ~/.claude/settings.json 2>/dev/null
```

Report: model, permissions mode, custom settings.

## Output Format

```
┌─────────────────────────────────────────────────────┐
│  POS AUDIT · {date}                                  │
│  working dir: {cwd}                                  │
└─────────────────────────────────────────────────────┘

  CONSTITUTION                                    {score}
  ├─ CLAUDE.md (global)     {lines}L  {status}
  ├─ CLAUDE.md (project)    {lines}L  {status}
  └─ AGENTS.md              {status}

  SKILLS                                          {count}
  ├─ Global: {list}
  └─ Project: {list}

  MCP SERVERS                                     {count}
  ├─ {server name}          {type}
  └─ {server name}          {type}

  MEMORY                                          {files}
  ├─ Auto memory            {count} files, {size}
  └─ Episodic               {status}

  HOOKS                                           {count}
  └─ {hook description}

  ─────────────────────────────────────────────────

  POS SCORE: {score}/10

  GAPS (what to add next):
  1. {most impactful missing component}
  2. {second suggestion}
  3. {third suggestion}
```

## Scoring

| Component | Points | Criteria |
|-----------|--------|----------|
| CLAUDE.md exists | 1 | Any CLAUDE.md |
| CLAUDE.md > 50 lines | 1 | Meaningful rules |
| Skills > 0 | 1 | Has any skills |
| Skills > 5 | 1 | Meaningful skill library |
| MCP > 0 | 1 | Has any MCP servers |
| MCP > 2 | 1 | Multiple integrations |
| Memory active | 1 | Auto memory exists |
| Hooks configured | 1 | Any hooks |
| AGENTS.md | 1 | Project has agent index |
| Project CLAUDE.md | 1 | Project-specific rules |

## Gap Suggestions

Based on what's missing, suggest the highest-impact next step:

- No CLAUDE.md → "Create ~/.claude/CLAUDE.md with your basic rules and preferences"
- No skills → "Create your first skill: /pos-morning for a daily brief pipeline"
- No MCP → "Add filesystem MCP server for file access outside working directory"
- No memory → "Enable auto memory by creating ~/.claude/projects/*/memory/"
- No hooks → "Add a PostToolUse hook for logging or notifications"
- Score < 3 → "Start with CLAUDE.md + 1 skill + 1 MCP server — minimum viable POS"
- Score 3-6 → "Add more skills and connect more data sources via MCP"
- Score 7-9 → "Add hooks and proactive scheduling (cron + claude -p)"
- Score 10 → "You have a full POS! Consider building a dashboard or sharing your setup"
