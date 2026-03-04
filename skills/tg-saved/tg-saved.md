---
description: "Telegram Saved Messages → Deep Analysis → Obsidian notes"
allowed-tools: "Bash, Read, Write, Edit, Glob, Agent, AskUserQuestion"
---

# TG Saved v2 — Deep Analysis с URL-парсингом

Extract Telegram Saved Messages, deeply analyze each one using Claude CLI subprocess, and save as rich Obsidian notes.

## Instructions

When the user runs `/tg-saved`, follow these steps:

### Step 1: Extract messages

Parse `$ARGUMENTS`:
- Number = days to look back (default: 30)
- `--all` = process ALL messages, ignoring deduplication state

Run the extraction script:

```bash
python3 scripts/tg_saved_extract.py --days <N>
```

Or with `--all` to re-process everything:
```bash
python3 scripts/tg_saved_extract.py --days <N> --all
```

**Deduplication**: The script automatically skips messages that were already processed in previous runs (tracked in `processed_ids.json`). Only NEW messages are returned.

### Step 2: Read the JSON output

Read the file `/tmp/tg_saved_output.json`. It contains an array of messages with fields:
- `id`, `date`, `text`, `media_type`, `forward_from`, `urls`
- Optional: `webpage_title`, `webpage_description`
- `url_contents` — array of `{url, title, content}` with fetched page text (up to 5000 chars each)

### Step 3: Filter messages

Skip messages that are:
- Empty or only media without text
- Very short without meaningful content (< 10 characters)
- Pure credentials/config without context

### Step 4: Analyze EACH message via Claude CLI

For each non-skipped message, run deep analysis using `claude` CLI subprocess:

```bash
echo '<PROMPT>' | claude -p --model sonnet
```

The prompt instructs Claude to:
1. Determine content type: find, note, article, guide, resource
2. Create a short Russian title (2-5 words)
3. Determine 1-3 topic tags
4. Write a detailed analysis with sections: Что это → Ключевые возможности → Инсайты → Сильные стороны → Слабые стороны → Вердикт

### Step 5: Create Obsidian notes

For each analyzed message, create a note with:
- YAML frontmatter (tags, date, source_channel, url)
- Full analysis body
- Links section
- Original message text

### Step 6: Mark messages as processed

After ALL notes are created:
```bash
python3 scripts/tg_saved_extract.py --mark-processed
```

This prevents re-processing on next run.

## Arguments

- `/tg-saved` → last 30 days, only new messages
- `/tg-saved 7` → last 7 days, only new
- `/tg-saved --all` → re-process ALL
- `/tg-saved 7 --all` → last 7 days, re-process ALL
