# POS Starter Pack — CTRL

5 skills to bootstrap your Personal Operating System with Claude Code. Based on real production patterns — not generic templates.

## What Is a POS?

A **Personal Operating System** is the infrastructure that makes Claude Code work FOR you proactively:

```
Context (CLAUDE.md)     → who you are, your rules and conventions
  └─ MCP servers        → data connections (calendar, tasks, search, messaging)
    └─ Skills           → reusable workflows as markdown files
      └─ Hooks          → automation triggers (session start/end, file writes)
        └─ Operations   → daily rituals (morning brief, ambient research, quality eval)
          └─ Dashboard  → visual snapshot of your system
```

Each layer builds on the previous. You can stop at any layer and have a working system.

## What's Inside

| Skill | What it does | Pattern |
|-------|-------------|---------|
| `/pos-setup` | **Start here.** 6-phase pipeline — builds your POS from zero with auto-detection | Orchestrator |
| `/pos-audit` | Scan your setup — score 0-12 with gap analysis across 6 layers | A: Audit |
| `/pos-morning` | Morning brief — calendar + tasks + sessions → ONE focus sentence | B: Pipeline |
| `/pos-dashboard-gen` | Generate terminal-aesthetic HTML dashboard from your context | C: Generator |
| `/pos-skill-factory` | Create new skills from natural language using 4 template patterns | Meta |

## Quick Install

```bash
# Clone and install all 5 skills
git clone https://github.com/ai-mindset-org/pos-sprint.git /tmp/pos-sprint
bash /tmp/pos-sprint/skill-pack/install.sh

# Or one-liner without clone:
for skill in pos-setup pos-morning pos-audit pos-skill-factory pos-dashboard-gen; do
  mkdir -p ~/.claude/skills/$skill
  cp /tmp/pos-sprint/skill-pack/$skill/SKILL.md ~/.claude/skills/$skill/SKILL.md
done
```

Or manually: copy any SKILL.md into `~/.claude/skills/{name}/SKILL.md`.

## Recommended Order

1. **`/pos-setup`** — the wizard detects your state and guides through each phase
2. **`/pos-audit`** — if you already have some setup and want your score
3. **`/pos-morning`** — get your first daily brief (the "aha moment")
4. **`/pos-dashboard-gen`** — see your POS as a visual dashboard
5. **`/pos-skill-factory`** — create skills for YOUR workflows

## The "Aha Moment"

The turning point for POS adoption is the **first proactive agent action**. Running `/pos-morning` and seeing all your data sources (calendar, tasks, sessions, messages) synthesized into ONE focus sentence — that's when it clicks. Prioritize getting to this moment.

## MCP Integration Map

Skills auto-detect your MCP servers and adapt. Here's what each server enables:

| MCP Server | Category | What It Unlocks |
|-----------|----------|-----------------|
| **Linear** | Tasks | Task tracking, sprint view, `/linear-action`, Linear Awareness Layer |
| **Krisp** | Meetings | Transcripts, action items, yesterday's calls in morning brief |
| **Telegram** | Messaging | Brief delivery, team comms, saved messages as context |
| **Exa** | Search | `/research` skill, `/ambient-advisor`, fact-checking |
| **Playwright** | Browser | Screenshots, visual cards, web verification |
| **filesystem** | Files | Cross-project file access, vault operations |
| **context7** | Docs | Up-to-date library documentation |
| **Notion** | Notes | Knowledge base queries, database access |
| **Netlify** | Deploy | CI/CD management from terminal |

**No servers required** — skills degrade gracefully. Zero MCP = minimal but working system. Each server you add unlocks more capability.

## Skill Patterns

Every skill in the ecosystem follows one of 4 patterns:

| Pattern | Structure | When to Use |
|---------|-----------|-------------|
| **A: Audit** | scan → score → suggest | Examining systems, health checks |
| **B: Pipeline** | detect → gather → synthesize → output | Pulling from sources, creating briefs |
| **C: Generator** | input → transform → write | Producing files and artifacts |
| **D: Integrator** | MCP → payload → preview → execute | Wrapping external services |

Use `/pos-skill-factory` to create skills in any pattern.

## Hooks (Automation Layer)

Real hook patterns that make the POS proactive:

| Hook | Trigger | What It Does |
|------|---------|--------------|
| Linear Awareness | SessionStart | Shows relevant task context at session start |
| Ambient Research | SessionStart | Auto-triggers background Exa search on strategic topics |
| Open in Obsidian | PostToolUse:Write | Auto-opens .md files in Obsidian after writing |
| Session Logging | SessionEnd | Logs Linear task references for cross-session tracking |

`/pos-setup` Phase 4 guides through hook installation.

## Naming Convention

The recommended file naming format for POS artifacts:

```
{project} {type} description – YYYY-MM-DD.md
```

Rules:
- EN DASH (–) only — never em dash (—) or hyphen (-)
- Date ALWAYS at the end
- Types: `research`, `analysis`, `draft`, `rule`, `meeting`, `summary`, `guide`, `prd`, `skill`
- YAML frontmatter required

## Requirements

- Claude Code (any version with skills support)
- No MCP servers required (skills adapt to what's available)
- Optional: Linear, Krisp, Telegram, Exa, Playwright — each unlocks more data

## Philosophy

- **Works with zero setup** — adapts to whatever you have
- **Plain text** — skills are markdown files, edit them freely
- **Terminal aesthetic** — monospace, dark theme, box-drawing characters
- **Composable** — each skill is independent, combine as you like
- **Real patterns** — every recommendation tested in production use
- **Graceful degradation** — missing MCP = skip, not error

## Name: CTRL

The skill pack identity is **CTRL** (control center). Terminal log entries use the `ctrl >` prefix.
