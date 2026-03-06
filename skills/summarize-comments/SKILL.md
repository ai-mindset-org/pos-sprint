---
name: summarize-comments
description: >
  Делает LLM-выжимку из комментариев менеджеров об одном или нескольких
  подрядчиках. Используй этот скилл когда нужно понять что говорят менеджеры
  о конкретном подрядчике, или получить JSON с выжимкой для дальнейшей
  обработки.
user-invocable: true
argument-hint: "<email подрядчика> или <путь к Agent2 JSON>"
allowed-tools: Bash, Read, Write, mcp__baserow__list_rows
---

# summarize-comments — Выжимка отзывов менеджеров

## Определи входные данные

- Если `$ARGUMENTS` содержит `@` — это email одного подрядчика.
- Если `$ARGUMENTS` — путь к файлу — прочитай его через Read tool
  и извлеки emails из `top_candidates[].email`.

## Шаг 1: Загрузи данные из Reliability Forms

```
mcp__baserow__list_rows(table_id=<BASEROW_RELIABILITY_FORM_TABLE_ID>)
```

Отфильтруй строки по нужным emails (поле `Vendor`).

Поля для анализа:
- `За что можно похвалить`
- `За что можно поругать`
- `Дополнительная информация`
- `TotalScore`, `Likes` — числовые оценки

## Шаг 2: Сформируй LLM-выжимку

Для каждого подрядчика:
- **summary** — 1-2 предложения общего характера
- **highlights_llm** — 2-3 конкретных сильных стороны
- **risks_llm** — конкретные риски (если есть)
- **sentiment** — positive / neutral / negative
- **avg_score**, **avg_likes** — среднее по числовым полям
- **source_count** — количество отзывов

Правила: только реальные данные. При < 2 отзывов пиши «Недостаточно данных».
При противоречиях — отмечай их явно.

## Шаг 3: Выведи JSON и резюме

Выведи JSON в чате:
```json
{
  "summaries": [
    {
      "email": "vendor@example.com",
      "source_count": 6,
      "sentiment": "positive",
      "summary": "...",
      "highlights_llm": ["...", "..."],
      "risks_llm": ["..."],
      "avg_score": 85.0,
      "avg_likes": 8.5
    }
  ]
}
```

Сохрани JSON в файл:
```bash
cat > /tmp/comments_summary.json << 'EOF'
{ ... }
EOF
```

Также выведи человекочитаемое резюме для каждого подрядчика.
