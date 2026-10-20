# Naming Convention & Vault Structure

> Стартовый гайд: как называть файлы, организовать Obsidian vault и подружить всё это с AI-агентами.
>
> **POS Sprint** — AI Mindset, март 2026

---

## Содержание

- [Формула](#формула)
- [Типы контента](#типы-контента-type)
- [Проектные коды](#проектные-коды-project)
- [Структура vault](#структура-vault)
- [YAML Frontmatter](#yaml-frontmatter)
- [Теги](#теги)
- [Плагины](#плагины--минимальный-набор)
- [AI-агенты и CLAUDE.md](#интеграция-с-ai-агентами)
- [Установка — 4 уровня](#установка--4-уровня)
- [Примеры](#примеры)
- [Антипаттерны](#антипаттерны)
- [Быстрый старт — 15 минут](#быстрый-старт--15-минут)

---

## Формула

```
{project} {type} описание – YYYY-MM-DD.md
```

| Элемент | Что | Пример |
|---------|-----|--------|
| `{project}` | Код проекта | `{startup}`, `{channel}`, `{self}` |
| `{type}` | Тип контента | `{research}`, `{guide}`, `{plan}` |
| описание | Краткое название, 3–7 слов | `анализ конкурентов EdTech` |
| `– YYYY-MM-DD` | Дата через EN DASH | `– 2026-03-04` |

### Правила

- **EN DASH `–`** — единственное тире. Mac: `Option + -`. Windows: `Alt + 0150`.
- **Дата — в конце.** Всегда. `{project} {research} тема – 2026-03-04.md` — да. `{project} {2026-03-04} тема.md` — нет.
- **Максимум 80 символов** — для терминала, Git, мобильных.
- **Максимум 2 кода** в фигурных скобках перед описанием.

---

## Типы контента {type}

Начните с 5–7 типов. Добавляйте по мере потребности.

### Базовые

| Тип | Для чего |
|-----|----------|
| `{rule}` | Правила, стандарты |
| `{guide}` | Инструкции, how-to |
| `{research}` | Исследования, анализ |
| `{plan}` | Планы, roadmap |
| `{template}` | Шаблоны |
| `{prompt}` | Промпты для AI |
| `{tool}` | Описание инструмента |

### Встречи

| Тип | Для чего |
|-----|----------|
| `{transcript}` | Транскрипт звонка |
| `{summary}` | Саммари встречи |
| `{meeting}` | Запись встречи |

### Контент

| Тип | Для чего |
|-----|----------|
| `{article}` | Статья, пост |
| `{demo}` | Демонстрация |
| `{case}` | Практический кейс |

### Процессы

| Тип | Для чего |
|-----|----------|
| `{daily-focus}` | Фокус дня |
| `{weekly-sync}` | Еженедельный обзор |
| `{retro}` | Ретроспектива |
| `{prd}` | Product Requirements |

---

## Проектные коды {project}

Короткий идентификатор (2–8 символов), уникальный, стабильный.

```
{startup}       — основной бизнес
{product}       — конкретный продукт
{consulting}    — консалтинг
{channel}       — канал, блог
{course}        — образовательный проект
{self}          — личное развитие
{team}          — командные документы
```

**Как создать свой:** выберите короткое слово → запишите в `{rule} project codes.md` → используйте во всех файлах проекта.

---

## Структура vault

### Базовая (старт)

```
vault/
├── _inbox/          ← всё новое сюда
├── _templates/      ← шаблоны
├── projects/        ← по проектам
│   ├── {project-a}/
│   └── {project-b}/
├── meetings/        ← транскрипты, саммари
├── rules/           ← правила, конвенции
├── articles/        ← контент
└── resources/       ← справочные материалы
```

### Расширенная (200+ файлов)

```
vault/
├── _inbox/
├── _templates/
├── projects/
│   └── {startup}/
│       ├── artifacts/    ← готовые артефакты
│       ├── sources/      ← транскрипты, данные
│       └── results/      ← feedback, retro
├── meetings/
├── rules/
├── articles/
├── @people/             ← карточки людей (CRM)
├── daily/               ← ежедневные фокусы
└── archive/             ← завершённые проекты
```

### Принципы

- **6–10 папок** на верхнем уровне — норма. 30 — хаос.
- **Flat > nested.** Один уровень лучше трёх.
- **Файл живёт по контексту,** не по типу. Тип — в имени.
- **AGENTS.md** в каждой значимой папке — индекс для AI-агентов.

---

## YAML Frontmatter

### Минимальный

```yaml
---
tags:
  - type/research
  - project/startup
date: 2026-03-04
---
```

### Полный

```yaml
---
tags:
  - type/research
  - project/startup
  - topic/market-analysis
  - status/active
date: 2026-03-04
status: active
refs:
  - "[[{startup} {plan} MVP roadmap – 2026-02-20]]"
author: Your Name
---
```

---

## Теги

**Принцип:** теги дополняют имя файла, не дублируют. 3–5 тегов на файл — норма.

```
type/           ← тип (type/research, type/guide)
project/        ← проект (project/startup)
topic/          ← тема (topic/automation)
status/         ← статус (status/active, status/draft)
```

### Когда что

| Механизм | Для чего |
|----------|---------|
| **Папки** | Физическое расположение |
| **Теги** | Невидимые измерения, фильтрация |
| **Ссылки `[[]]`** | Смысловые связи |
| **Имя файла** | Контекст с первого взгляда |

---

## Плагины — минимальный набор

### Ставьте сразу

| Плагин | Зачем |
|--------|-------|
| **Templater** | Шаблоны с переменными |
| **Calendar** | Навигация по дням |
| **Quick Switcher++** | Поиск файлов |
| **Dataview** | Запросы к vault |

### По мере роста

Periodic Notes, Tag Wrangler, Linter, Smart Connections.

### Не ставьте сразу

Fancy themes (отвлекают), Kanban/Database (overhead), Publish (рано).

---

## Интеграция с AI-агентами

AI-агент работает с vault как с кодовой базой. Хорошее имя файла = агент понимает контекст.

### CLAUDE.md

Создайте в корне vault — агент будет следовать этим правилам:

```markdown
# Vault Rules

## Naming Convention
When creating new files, follow this format:
{project} {type} description – YYYY-MM-DD.md

## Active Projects
- {startup} — main business
- {consulting} — client projects
- {channel} — blog content

## File Types
- {research} — analysis
- {guide} — howtos
- {rule} — standards
- {plan} — roadmaps
- {article} — publications

## Folder Rules
- New files go to _inbox/ unless project is specified
- Never create new top-level folders
- Use naming convention instead of deep nesting

## Tags
Use: type/, project/, topic/, status/
Max 5 tags per file. YAML frontmatter always.
```

> Тот же подход работает с `.cursorrules` (Cursor) и `codex.md` (Codex).

---

## Установка — 4 уровня

### Уровень 0 — скачайте и начните
Скачайте этот файл → положите в `rules/` → сверяйтесь с формулой при создании файлов.

### Уровень 1 — попросите AI адаптировать
Откройте любой AI-чат, вставьте этот гайд + список своих проектов. Попросите: «Адаптируй конвенцию, предложи project codes и структуру папок.»

### Уровень 2 — Claude Code / Codex / Cursor
Скачайте файл в vault + создайте `CLAUDE.md` (шаблон выше). Агент автоматически создаёт файлы в правильном формате.

### Уровень 3 — полная POS
Структура папок + CLAUDE.md + Skills + Templater + AGENTS.md + ежедневные ритуалы.

---

## Примеры

### Стартап

```
{product} {prd} уведомления v2 – 2026-02-15.md
{product} {research} паттерны Q1 – 2026-03-01.md
{product} {plan} roadmap Q2 – 2026-03-10.md
{product} {retro} спринт 04 – 2026-02-28.md
```

### Консалтинг

```
{client-a} {summary} стратсессия – 2026-02-20.md
{consulting} {template} proposal – 2026-01-15.md
{consulting} {rule} онбординг – 2026-01-10.md
```

### Контент

```
{channel} {article} утренние ритуалы – 2026-03-01.md
{podcast} {transcript} выпуск 12 – 2026-02-18.md
{content} {research} тренды AI – 2026-03-02.md
```

### Личное

```
{self} {daily-focus} 2026-03-04 Tuesday.md
{self} {weekly-sync} 2026-W10 – 2026-03-03.md
{self} {plan} цели Q2 – 2026-03-15.md
```

---

## Антипаттерны

| Не делайте | Почему | Делайте |
|------------|--------|---------|
| `Meeting notes 23.docx` | Нет контекста | `{project} {meeting} тема – дата.md` |
| `FINAL_v3_РЕАЛЬНО_ФИНАЛ` | Версии в имени | `version:` в YAML |
| 5 уровней папок | Не найдёте ничего | Flat + naming convention |
| 50 тегов на файл | Бесполезно | 3–5 тегов |
| Дата в середине имени | Ломает сортировку | Дата в конце |
| 150+ символов | Обрезается | Максимум 80 |

---

## Быстрый старт — 15 минут

- [ ] **Файл правил** — `rules/{rule} naming convention.md` с формулой и кодами (2 мин)
- [ ] **3 проекта** — придумайте коды (2 мин)
- [ ] **5 типов** — из списка выше (1 мин)
- [ ] **CLAUDE.md** — в корне vault (5 мин)
- [ ] **Переименуйте 5 файлов** — по новой конвенции (5 мин)

### Эволюция

| Файлов | Что добавлять |
|:------:|--------------|
| 0–50 | Базовая структура, 3 проекта, 5 типов |
| 50–200 | Templater, теги, daily focus |
| 200–500 | Dataview, weekly sync, AGENTS.md |
| 500+ | Skills, автоматизация, AI-интеграция |

> **Правило:** не добавляйте сложность, пока не почувствовали потребность.

---

<sub>POS Sprint — AI Mindset · [aimindset.org](https://aimindset.org) · 2026</sub>
