# Продвинутый CLAUDE.md — полная экосистема

> Пример CLAUDE.md с контекстным footer, self-eval, Linear awareness и правилами поведения.
> Адаптируй под свой стек и инструменты.

---

## Response Style

- Отвечай по-русски (технические термины — на английском)
- Используй markdown с **bold** для ключевых терминов
- Не добавлять комментарии к очевидному коду
- Не добавлять docstrings если не просят

## Context Management Protocol

### Footer (ОБЯЗАТЕЛЬНО в каждом содержательном ответе)

**Формат:**
```
◇ ctx: {used}K | {left}K left | {pct}% | {symbol}
▫ eval: T:✓ R:✓ C:○
```

**Символы:**
- `●` — OK (< 50%)
- `◐` — WARN (50–70%) + compact mode
- `○` — CRIT (> 70%) + handoff

**Данные:** бери из Status Line (▰▰▰▱▱ XX%).

### Поведение по порогам

| Порог | Режим | Что делать |
|-------|-------|------------|
| < 50% | ● OK | Полный функционал |
| 50–70% | ◐ WARN | Компактные ответы |
| > 70% | ○ CRIT | Только handoff |

## AI Evals Protocol

В конце каждого ответа (после ctx):

```
▫ eval: T:✓ R:✓ C:○
```

| Область | Что оценивает |
|---------|---------------|
| T (Text) | Структура, ясность, полезность |
| R (Rules) | Следование правилам CLAUDE.md |
| C (Code) | Работает, минимализм, идиоматичность |

**Легенда:** `✓` Pass · `✗` Fail · `○` N/A

## Task Awareness Layer

Если при запуске сессии получены задачи — показывать в footer:

```
▫ linear: TASK-ID · описание · ◐ IP
```

**Символы:** `◐` In Progress · `○` Todo · `●` Done · `◑` In Review

Показывать только при наличии match с текущей сессией.

## Code Standards

- **Стек:** TypeScript, React, Tailwind
- **Тесты:** vitest
- **Линтинг:** ESLint + Prettier
- Prefer editing existing files over creating new ones
- Don't add features beyond what was asked

## File Management

- Никогда не создавать новые папки
- Файлы: `{project} {type} description – YYYY-MM-DD.md`
- YAML frontmatter с tags обязателен
