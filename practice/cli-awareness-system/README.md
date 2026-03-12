# CLI Awareness System — настройка информационного слоя в Claude Code

> Как превратить терминал из чёрного ящика в панель управления, которая показывает контекст, задачи и состояние сессии — без переключения между приложениями.

## Зачем это нужно

Claude Code работает в терминале. По умолчанию ты видишь только текст ответов. Но CLI умеет гораздо больше — показывать процент использованного контекста, текущие задачи из таск-менеджера, статус фоновых процессов, и автоматически менять поведение когда контекст заканчивается.

Это не один инструмент, а **система из нескольких слоёв**, каждый из которых можно внедрить отдельно.

---

## Архитектура: 4 слоя осведомлённости

```
┌─────────────────────────────────────────────────┐
│  Level 4: Mission Control                       │
│  iTerm2 status bar + внешний JSON state         │
├─────────────────────────────────────────────────┤
│  Level 3: Awareness Layers                      │
│  Linear/Jira/Todoist интеграция в footer        │
├─────────────────────────────────────────────────┤
│  Level 2: Response Footer Protocol              │
│  ctx + eval + status в каждом ответе            │
├─────────────────────────────────────────────────┤
│  Level 1: Status Line                           │
│  Bash-скрипт → модель, контекст, проект         │
└─────────────────────────────────────────────────┘
```

**Каждый уровень работает независимо.** Можно начать с Level 1 и добавлять остальные по мере необходимости.

---

## Быстрый старт: какой уровень тебе подходит?

### Анкета

Ответь на вопросы — они покажут, с какого уровня начать:

| # | Вопрос | Да → уровень |
|---|--------|--------------|
| 1 | Хочу видеть сколько контекста осталось прямо в терминале? | **Level 1** |
| 2 | Хочу чтобы Claude сам писал в конце ответа сколько контекста осталось? | **Level 2** |
| 3 | Использую таск-менеджер (Linear, Jira, Todoist) и хочу видеть задачи прямо в CLI? | **Level 3** |
| 4 | Работаю в iTerm2 и хочу видеть состояние Claude в статус-баре терминала? | **Level 4** |
| 5 | Хочу чтобы Claude менял поведение когда контекст заполнен на 70%+? | **Level 2** |
| 6 | Хочу получать уведомления о фоновых задачах (background research)? | **Level 1 + 4** |
| 7 | Работаю с несколькими проектами и хочу разные настройки для каждого? | **Level 1** (presets) |

**Рекомендация:** начни с Level 1 + Level 2. Это занимает 10 минут и даёт 80% пользы.

---

## Level 1: Status Line

**Что это:** строка внизу терминала Claude Code, которая показывает модель, проект и процент контекста в реальном времени.

**Как выглядит:**
```
⏵ notes │ ◆ Opus 4.6 │ ▰▰▰▱▱▱▱▱▱▱ 32% ◇68k │ ◐AIM-2054 │ 11m
```

**Расшифровка:**
- `⏵ notes` — текущий проект (определяется по рабочей директории)
- `◆ Opus 4.6` — модель (◆ Opus, ■ Sonnet, ▪ Haiku)
- `▰▰▰▱▱▱▱▱▱▱ 32%` — использование контекстного окна
- `◇68k` — токены из кэша (экономия)
- `◐AIM-2054` — текущая задача из Linear (если настроен Level 3)
- `11m` — длительность сессии

### Настройка (5 минут)

**1. Создай скрипт:**

```bash
mkdir -p ~/.claude
```

Создай файл `~/.claude/statusline.sh`:

```bash
#!/bin/bash
# Minimal Status Line for Claude Code

read -r json
command -v jq &>/dev/null || { echo "▪ jq?"; exit 0; }

model=$(echo "$json" | jq -r '.model.display_name // "—"')
model_id=$(echo "$json" | jq -r '.model.id // ""')
project_dir=$(echo "$json" | jq -r '.workspace.project_dir // .cwd // ""')
ctx_used=$(echo "$json" | jq -r '.context_window.used_percentage // 0' | xargs printf "%.0f" 2>/dev/null)
cache_read=$(echo "$json" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
duration_ms=$(echo "$json" | jq -r '.cost.total_duration_ms // 0')

dir_name=$(basename "$project_dir" 2>/dev/null)
cache_k=$((cache_read / 1000))
duration_min=$((duration_ms / 60000))

# Model symbol
case "$model_id" in
    *opus*)   model_sym="◆" ;;
    *sonnet*) model_sym="■" ;;
    *haiku*)  model_sym="▪" ;;
    *)        model_sym="○" ;;
esac

# Progress bar
filled=$(( (ctx_used + 5) / 10 ))
[ "$filled" -gt 10 ] && filled=10
bar=""
for ((i=0; i<filled; i++)); do bar+="▰"; done
for ((i=filled; i<10; i++)); do bar+="▱"; done

# Output
out="${dir_name} │ ${model_sym} ${model} │ ${bar} ${ctx_used}%"
[ "$cache_k" -gt 10 ] && out+=" ◇${cache_k}k"
[ "$duration_min" -gt 0 ] && out+=" │ ${duration_min}m"
echo "$out"
```

**2. Сделай исполняемым:**

```bash
chmod +x ~/.claude/statusline.sh
```

**3. Подключи в settings.json:**

Открой `~/.claude/settings.json` и добавь:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}
```

**4. Перезапусти Claude Code.** Готово — теперь внизу терминала будет строка с контекстом.

### Зависимости

- `jq` — парсер JSON. Установить: `brew install jq`

### Продвинутое: presets для разных проектов

Если работаешь с несколькими проектами, можно добавить router в конец скрипта:

```bash
case "$project_dir" in
    */my-saas-app*)
        # Custom output for your SaaS project
        echo "🚀 SaaS │ ${model_sym} ${model} │ ${bar} ${ctx_used}%"
        ;;
    */notes*|*/vault*)
        echo "📝 vault │ ${model_sym} ${model} │ ${bar} ${ctx_used}%"
        ;;
    *)
        echo "${dir_name} │ ${model_sym} ${model} │ ${bar} ${ctx_used}%"
        ;;
esac
```

### Доступные данные из JSON

Status Line получает JSON с полной информацией о сессии:

| Поле | Описание |
|------|----------|
| `.model.display_name` | Название модели (Opus 4.6) |
| `.model.id` | ID модели для case-match |
| `.workspace.project_dir` | Рабочая директория |
| `.context_window.used_percentage` | % использования контекста |
| `.context_window.context_window_size` | Размер окна в токенах |
| `.context_window.current_usage.cache_read_input_tokens` | Токены из кэша |
| `.cost.total_duration_ms` | Длительность сессии |
| `.cost.total_cost_usd` | Стоимость сессии в $ |

Полный список: `claude /statusline-setup` или [документация Claude Code](https://docs.anthropic.com/en/docs/claude-code).

---

## Level 2: Response Footer Protocol

**Что это:** инструкция в CLAUDE.md, которая заставляет Claude добавлять строку состояния в конце каждого ответа.

**Как выглядит:**
```
◇ ctx: 96K | 104K left | 48% | ●
▫ eval: T:✓ R:✓ C:○
```

**Расшифровка:**
- `◇ ctx:` — использование контекстного окна (K = тысячи токенов)
- `●` — режим OK (< 50%)
- `◐` — WARN (50–70%), компактные ответы
- `○` — CRIT (> 70%), только handoff
- `▫ eval:` — самооценка ответа (T=Text, R=Rules, C=Code)

### Настройка (3 минуты)

Добавь в свой `CLAUDE.md` (в корне проекта или `~/.claude/CLAUDE.md` глобально):

```markdown
## Context Management Protocol

### Footer (в каждом содержательном ответе)

Формат:
◇ ctx: {used}K | {left}K left | {pct}% | {symbol}

Символы:
- ● — OK (< 50%)
- ◐ — WARN (50–70%) + compact mode
- ○ — CRIT (> 70%) + handoff

Данные: бери из Status Line (▰▰▰▱▱ XX%).

### Поведение по порогам

| Порог | Режим | Что делать |
|-------|-------|------------|
| < 50% | OK | Полный функционал |
| 50–70% | WARN | Компактные ответы, экономить контекст |
| > 70% | CRIT | Только handoff — сохранить прогресс и передать контекст в новую сессию |

### При CRIT (> 70%)

Генерировать блок передачи:

## Handoff
**Проект:** [название]
**Сделано:** [что сделали]
**Осталось:** [что осталось]
**Prompt:** продолжи работу над...
```

### Опционально: Self-Eval

Если хочешь чтобы Claude оценивал качество ответов, добавь:

```markdown
## AI Evals Protocol

В конце каждого ответа:

▫ eval: T:✓ R:✓ C:○

- T (Text) — структура, ясность, actionable
- R (Rules) — следование правилам из CLAUDE.md
- C (Code) — работает, минимализм, идиоматичность
- ✓ = Pass, ✗ = Fail, ○ = N/A
```

### Зачем это работает

Claude Code видит Status Line процент контекста. Инструкция в CLAUDE.md говорит ему: "бери эти данные и показывай мне в footer". Модель послушно это делает, потому что CLAUDE.md — это её правила поведения.

**Ключевая идея:** ты не программируешь AI, а даёшь ему **инструкцию наблюдать за собой** и сообщать тебе о своём состоянии.

---

## Level 3: Awareness Layers (Task Manager Integration)

**Что это:** автоматическая привязка текущей сессии Claude Code к задачам из таск-менеджера. Claude видит свои задачи и показывает их в footer.

**Как выглядит:**
```
▫ linear: AIM-2054 · BOS speakers outreach · ◐ IP
```

**Символы статусов:** `◐` In Progress, `○` Todo, `●` Done, `◑` In Review

### Принцип работы

1. **SessionStart hook** — при запуске сессии скрипт читает кэш задач из memory-файла
2. **Context matching** — сопоставляет тему сессии с задачами (по названию, веткам git, контексту)
3. **Footer display** — инструкция в CLAUDE.md показывает задачу в каждом ответе
4. **SessionEnd hook** — при завершении записывает что было сделано

### Вариант A: Linear (через MCP)

**Требования:** Linear MCP server подключен к Claude Code.

**1. Создай memory-файл** для кэша задач:

```bash
mkdir -p ~/.claude/projects/YOUR-PROJECT/memory/
```

Создай `linear-tracking.md`:

```markdown
# Linear Task Cache

updated: 2026-03-12T10:00

## In Progress

#### AIM-123 · Описание задачи · IP
priority: Urgent

#### AIM-456 · Другая задача · IP
priority: Normal

## Todo (3)

#### AIM-789 · Будущая задача · Todo
```

**2. Создай SessionStart hook** — `~/.claude/hooks/linear-sync.sh`:

```bash
#!/usr/bin/env bash
# Linear Awareness — читает кэш задач при старте сессии
set -eo pipefail

MEMORY_FILE="$HOME/.claude/projects/YOUR-PROJECT/memory/linear-tracking.md"
[[ -f "$MEMORY_FILE" ]] || exit 0

CONTENT=$(<"$MEMORY_FILE")

# Извлечь IP задачи
IP_TASKS=$(echo "$CONTENT" | grep -E '^#### .+ · IP$' | sed 's/^#### //' | head -5)
IP_COUNT=$(echo "$CONTENT" | grep -cE '^#### .+ · IP$' || echo "0")

[[ $IP_COUNT -gt 0 ]] || exit 0

echo "--- Linear Awareness Layer ---"
echo "Tasks: ${IP_COUNT} In Progress"
echo "$IP_TASKS"
echo "--- End Linear ---"
```

```bash
chmod +x ~/.claude/hooks/linear-sync.sh
```

**3. Подключи hook** в `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/linear-sync.sh"
          }
        ]
      }
    ]
  }
}
```

**4. Добавь footer-инструкцию** в CLAUDE.md:

```markdown
## Linear Awareness Layer

В каждом ответе, если есть связанная задача:

▫ linear: AIM-XXXX · описание · ◐ IP

Символы: ◐ In Progress, ○ Todo, ● Done
Показывать только при наличии match.
```

### Вариант B: Todoist / Jira / любой таск-менеджер

Принцип тот же — разница только в формате кэша и способе синхронизации:

**Todoist:** используй Todoist MCP или API → записывай в memory-файл
**Jira:** используй Jira MCP (см. скилл jira-monitor в этом репо) → аналогичный hook
**Notion:** используй Notion MCP → фильтруй по assigned to me

**Универсальный шаблон memory-файла:**

```markdown
# Task Cache

updated: YYYY-MM-DDTHH:MM
source: todoist|jira|notion|linear

## Active

#### TASK-ID · Description · Status
priority: high|medium|low
```

### Синхронизация кэша

Кэш обновляется двумя способами:

1. **Ручной** — запустить скрипт синхронизации или обновить файл
2. **Автоматический** — SessionStart hook проверяет возраст кэша и предупреждает если stale (>4h)

Для автоматического обновления через MCP добавь в hook:

```bash
# Проверка возраста кэша
UPDATED=$(grep -m1 '^updated:' "$MEMORY_FILE" | sed 's/^updated://')
AGE_HOURS=$(( ($(date +%s) - $(date -j -f "%Y-%m-%dT%H:%M" "$UPDATED" "+%s")) / 3600 ))

if [[ $AGE_HOURS -gt 4 ]]; then
    echo "⚠ task cache stale (${AGE_HOURS}h) — sync recommended"
fi
```

---

## Level 4: Mission Control (iTerm2 Status Bar)

**Что это:** вынос данных Claude Code в нативный статус-бар iTerm2 — видно даже когда скроллишь вверх.

**Как выглядит:** полоска внизу iTerm2 с процентом контекста, моделью и статусом фоновых задач.

### Принцип

Status Line скрипт (Level 1) пишет JSON в файл:

```bash
~/.config/iterm2-mission-control/context.json
```

Содержимое:
```json
{
  "percent": 32,
  "left_k": 128,
  "cache_k": 68,
  "model": "Opus 4.6",
  "project": "notes",
  "duration_min": 11,
  "ts": 1773308500
}
```

iTerm2 Python API читает этот файл и рендерит в status bar.

### Настройка

**1. Добавь запись JSON в свой statusline.sh:**

В конец скрипта, перед финальным echo:

```bash
# Write state for iTerm2 Mission Control
MC_DIR="$HOME/.config/iterm2-mission-control"
[ -d "$MC_DIR" ] || mkdir -p "$MC_DIR"

ctx_size=$(echo "$json" | jq -r '.context_window.context_window_size // 0')
left_k=$(( ctx_size * (100 - ctx_used) / 100000 ))

printf '{"percent":%d,"left_k":%d,"cache_k":%d,"model":"%s","project":"%s","duration_min":%d,"ts":%d}\n' \
    "$ctx_used" "$left_k" "$cache_k" "$model" "$dir_name" "$duration_min" "$(date +%s)" \
    > "$MC_DIR/context.json"
```

**2. Настрой iTerm2:**

- Preferences → Profiles → Session → Status bar → Configure
- Добавь компонент "Custom Script" → укажи Python-скрипт
- Или используй AutoLaunch: `~/Library/Application Support/iTerm2/Scripts/AutoLaunch/`

**3. Python-скрипт для iTerm2** (см. `examples/iterm2-mission-control.py`):

Скрипт читает `context.json` и обновляет status bar component каждые 5 секунд.

### Альтернатива: tmux status bar

Если не используешь iTerm2, можно вывести в tmux:

```bash
# В .tmux.conf
set -g status-right '#(cat ~/.config/iterm2-mission-control/context.json 2>/dev/null | jq -r "\"▰ \" + (.percent|tostring) + \"%% │ \" + .model")'
set -g status-interval 5
```

---

## Hooks: автоматизация событий сессии

Hooks — это shell-скрипты, которые выполняются при событиях в Claude Code.

### Доступные события

| Event | Когда | Что получает (stdin) |
|-------|-------|---------------------|
| `SessionStart` | Запуск сессии | `{ cwd, session_id }` |
| `SessionEnd` | Завершение сессии | `{ session_id, transcript_path, reason }` |
| `PostToolUse` | После вызова инструмента | `{ tool_name, tool_input, tool_output }` |

### Примеры полезных hooks

**Открывать созданные .md файлы в Obsidian:**

```bash
#!/bin/bash
# PostToolUse hook: открыть новый .md в Obsidian
VAULT_ROOT="/path/to/your/vault"
VAULT_NAME="your-vault"

fp=$(jq -r '.tool_input.file_path // empty')

if [[ "$fp" == *.md ]] && [[ -f "$fp" ]] && [[ "$fp" == "$VAULT_ROOT"/* ]]; then
    relative="${fp#$VAULT_ROOT/}"
    encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$relative'))")
    open "obsidian://open?vault=$VAULT_NAME&file=$encoded" 2>/dev/null
fi
exit 0
```

**Сохранять список сессий за день:**

```bash
#!/bin/bash
# SessionEnd hook: логировать завершённую сессию
TODAY=$(date +%Y-%m-%d)
LOG="$HOME/.claude/session-log-${TODAY}.md"

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty')

# Извлечь первое сообщение как тему
TOPIC=$(grep '"type":"user"' "$TRANSCRIPT" 2>/dev/null | head -1 | jq -r '.message.content | if type == "string" then . else .[0].text end' | head -c 60)

echo "| $(date +%H:%M) | $TOPIC | $SESSION_ID |" >> "$LOG"
```

### Подключение hooks

В `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "command": "~/.claude/hooks/your-hook.sh" }]
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "~/.claude/hooks/your-start-hook.sh" }]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "~/.claude/hooks/your-end-hook.sh" }]
      }
    ]
  }
}
```

`matcher` фильтрует по имени инструмента (для PostToolUse) или оставляется пустым для всех.

---

## CLAUDE.md: тонкая настройка поведения

`CLAUDE.md` — файл правил поведения Claude Code. Может быть:

- **Глобальный:** `~/.claude/CLAUDE.md` — для всех проектов
- **Проектный:** `./CLAUDE.md` в корне проекта — для конкретного проекта
- **Вложенный:** `./path/CLAUDE.md` — для поддиректории

### Что можно настроить

| Категория | Примеры |
|-----------|---------|
| **Стиль ответов** | Язык, форматирование, длина |
| **Правила кода** | Стек, паттерны, conventions |
| **Footer protocol** | Контекст, eval, задачи |
| **Поведение** | Когда спрашивать, когда делать |
| **Файловая система** | Naming conventions, куда класть файлы |
| **Интеграции** | MCP servers, API keys, tools |

### Минимальный рабочий CLAUDE.md

```markdown
# Project Rules

## Response Footer
В конце каждого ответа:
◇ ctx: {used}K | {left}K left | {pct}% | {●/◐/○}

## Стиль
- Отвечай по-русски
- Используй markdown
- Bold для ключевых терминов

## Код
- Стек: TypeScript, React, Tailwind
- Тесты: vitest
- Не добавлять комментарии к очевидному коду
```

### Продвинутый пример: полная экосистема

См. `examples/advanced-claude-md.md` — полный CLAUDE.md с контекстом, eval, Linear и hooks.

---

## Сводная таблица

| Компонент | Файлы | Сложность | Время | Зависимости |
|-----------|-------|-----------|-------|-------------|
| **Status Line** | `statusline.sh` + `settings.json` | ⬤○○ | 5 мин | jq |
| **Footer Protocol** | `CLAUDE.md` | ⬤○○ | 3 мин | — |
| **Self-Eval** | `CLAUDE.md` | ⬤○○ | 2 мин | — |
| **Task Awareness** | hook + memory file + `CLAUDE.md` | ⬤⬤○ | 15 мин | MCP server |
| **Obsidian Hook** | `open-in-obsidian.sh` | ⬤○○ | 3 мин | Obsidian |
| **Session Logger** | `save-sessions.sh` | ⬤⬤○ | 10 мин | jq |
| **Mission Control** | statusline extension + iTerm2 | ⬤⬤⬤ | 30 мин | iTerm2, Python |
| **Background Research** | hook + state file + statusline | ⬤⬤⬤ | 20 мин | Exa MCP |

---

## Рекомендуемый путь внедрения

```
Неделя 1:  Level 1 (Status Line) + Level 2 (Footer)
           ↓
Неделя 2:  Hooks (Obsidian, Session Logger)
           ↓
Неделя 3:  Level 3 (Task Awareness)
           ↓
Когда будет время:  Level 4 (Mission Control)
```

**Главный принцип:** не пытайся внедрить всё сразу. Начни с Status Line + Footer — это 8 минут настройки и моментальная обратная связь. Остальное добавляй когда почувствуешь потребность.

---

## Файлы в этой директории

```
cli-awareness-system/
├── README.md                          ← этот файл
└── examples/
    ├── statusline-minimal.sh          ← минимальный Status Line
    ├── statusline-full.sh             ← полный Status Line с presets
    ├── claude-md-footer.md            ← шаблон Footer Protocol для CLAUDE.md
    ├── claude-md-advanced.md          ← продвинутый CLAUDE.md
    ├── linear-sync-hook.sh            ← SessionStart hook для Linear
    ├── session-logger-hook.sh         ← SessionEnd hook для логирования
    ├── open-in-obsidian-hook.sh       ← PostToolUse hook для Obsidian
    └── settings-example.json          ← пример settings.json
```

---

## Ссылки

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [MCP Servers](https://modelcontextprotocol.io/)
- [POS Sprint Repo](https://github.com/ai-mindset-org/pos-sprint)
