---
description: "Автоматический дневной отчёт из activity log, git, sessions"
allowed-tools: "Bash, Read, Write, Edit, Glob, Agent"
---

# Daily Work — Автоматический дневной отчёт

Generate a comprehensive daily work report from activity log, git logs, and session data.

## Arguments

- `/daily-work` → report for today
- `/daily-work 2026-03-01` → report for specific date
- `/daily-work --weekly` → weekly digest (Mon-Sun)

## Step 1: Collect Data

**Activity Log**: Read `claude-activity.log`, filter by target date.
Format: `YYYY-MM-DDTHH:MM:SS|session_id|tool_name|target|detail`

**Git Logs**: Scan git log for each project directory (run in parallel):
```bash
git -C /path/to/project log --since="DATE 00:00" --until="DATE 23:59:59" --format="%H|%h|%s|%an|%ai" --all
```

**Session Checkpoints**: Read session files modified on target date.

## Step 2: Multi-Session Support

If report for the date already exists:
- Don't overwrite — add new `## Сессия N` section
- Recalculate Summary and analytics

## Step 3: Generate Report

Group activity by project. Calculate metrics:
- Total commits, files modified, sessions count
- Estimated time (first to last activity per session)
- Streak (consecutive days with reports)

**Quality rule**: Every action must be described in DETAIL — not just "created skill X", but full explanation of what, why, how.

## Step 4: Write Obsidian Note

Output: `~/Documents/Obsidian Vault/Daily Work/YYYY-MM-DD.md`

Format includes:
- YAML frontmatter with tags
- Summary (5-10 sentences)
- Per-session sections with project details
- Analytics table with metrics
- Achievements, Blockers, Insights
- AI Coach recommendations
- Learning Radar (relevant articles if blockers found)

## Step 5: Archive

Append summary to monthly archive `claude-mem-YYYY-MM.md`.

## Weekly Digest (`--weekly`)

Aggregates all daily reports for Mon-Sun into:
`~/Documents/Obsidian Vault/Daily Work/weekly/YYYY-WNN.md`
