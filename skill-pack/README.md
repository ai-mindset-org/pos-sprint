# POS Starter Pack — CTRL

4 skills to bootstrap your Personal Operating System with Claude Code.

## What's Inside

| Skill | What it does | Complexity |
|-------|-------------|------------|
| `/pos-audit` | Scan your setup — what POS components you have, score 0-10, gap suggestions | Instant |
| `/pos-morning` | Morning pipeline — calendar + tasks + sessions → daily brief | 30 sec |
| `/pos-dashboard-gen` | Generate a personal HTML dashboard from your context | 1 min |
| `/pos-skill-factory` | Create new skills from natural language descriptions | Interactive |

## Quick Install

```bash
# One-liner: copy all 4 skills to ~/.claude/skills/
for skill in pos-morning pos-audit pos-skill-factory pos-dashboard-gen; do
  mkdir -p ~/.claude/skills/$skill
  cp skill-pack/$skill/SKILL.md ~/.claude/skills/$skill/SKILL.md
done
```

Or manually: copy any SKILL.md you want into `~/.claude/skills/{name}/SKILL.md`.

## Recommended Order

1. **Start with `/pos-audit`** — see where you stand
2. **Run `/pos-morning`** — get your first daily brief
3. **Try `/pos-dashboard-gen`** — see your POS as a visual dashboard
4. **Use `/pos-skill-factory`** — create skills for YOUR workflows

## Requirements

- Claude Code (any version with skills support)
- No MCP servers required (skills adapt to what's available)
- Optional: Linear MCP, Telegram MCP, Google Calendar script — each unlocks more data

## Philosophy

- **Works with zero setup** — adapts to whatever you have
- **Plain text** — skills are markdown files, edit them freely
- **Terminal aesthetic** — monospace, dark theme, box-drawing characters
- **Composable** — each skill is independent, combine as you like

## Name: CTRL

The skill pack bot identity is **CTRL** (control center). Terminal log entries from dashboard actions use the `ctrl >` prefix. Name your dashboard agent whatever you want — CTRL is the default.
