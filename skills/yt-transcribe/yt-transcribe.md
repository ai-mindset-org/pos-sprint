---
description: "Транскрибировать YouTube-видео через Whisper и сохранить в Obsidian"
allowed-tools: "Bash, Read, Write, Edit, Glob, AskUserQuestion"
---

# YT Transcribe — YouTube → Whisper → Obsidian

Транскрибируй YouTube-видео и сохрани результат в Obsidian Vault.

**Аргумент:** `$ARGUMENTS` — YouTube URL

## Шаг 1: Транскрипция

Запусти скрипт транскрипции:

```bash
python3 scripts/yt_transcribe.py --url "$ARGUMENTS" --output /tmp
```

Скрипт скачает аудио, транскрибирует через Whisper large-v3, и сохранит сырой `.md` в `/tmp/`.

## Шаг 2: Презентация (опционально)

Спроси пользователя: есть ли презентация (PDF/PPTX)?

- **PDF** → `pdftoppm` конвертирует слайды в PNG, `pdftotext` извлекает текст
- **PPTX** → `python-pptx` извлекает текст слайдов
- Сопоставь слайды с моментами транскрипта по контексту и таймкодам

## Шаг 3: Обработка транскрипта

1. Разбей на логические секции с заголовками `##` и `###`
2. Сохрани таймкоды `[MM:SS]` в начале каждого абзаца
3. Форматирование: код в блоках, термины жирным, списки
4. Привязка слайдов (если есть)
5. Секция `## Key Takeaways` в конце

## Шаг 4: Сохранение в Obsidian

Всегда создавай **два файла**:

1. **Транскрипт**: `{проект} {transcript} описание – YYYY-MM-DD – Claude Code.md`
2. **Саммери**: `{проект} {summary} описание – YYYY-MM-DD – Claude Code.md`
3. (Опционально) **Слайды**: `{проект} {slides} PREFIX Презентация – YYYY-MM-DD.md`

## Шаг 5: Cleanup

Удали временные файлы из `/tmp/`.
