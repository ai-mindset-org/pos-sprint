---
name: find-vendor
description: >
  Единый оркестратор поиска подрядчика. Принимает запрос на естественном языке,
  конвертирует его в JSON, фильтрует и ранжирует подрядчиков из Baserow,
  суммирует отзывы через LLM и показывает результат в чате.
  Используй этот скилл когда менеджер описывает, какой специалист ему нужен.
user-invocable: true
argument-hint: "<запрос на естественном языке>"
allowed-tools: Bash, Read, Write, mcp__baserow__list_rows
---

# find-vendor — Поиск подрядчика

## Шаг 1: Разбор запроса (NL → JSON)

Прочитай запрос из `$ARGUMENTS` или из диалога и сгенерируй JSON,
соответствующий `schemas/agent1_output.schema.json`.

**Обязательные поля** (если не указаны — задай уточняющие вопросы, не переходи дальше):
- `source` — язык оригинала (формат: `en_us`, `de_de`, ...)
- `target` — язык перевода
- `type` — тип услуги: `Translation`, `Editing`, `Proofreading`

**Псевдонимы типов:**
- Translation: перевод, translation, перевести
- Editing: редактура, редактирование, editing
- Proofreading: вычитка, proofreading

**Псевдонимы доменов:** MMO, Warhammer, MTPE, Юридичка/юрид, Шутеры

**Значения по умолчанию:**
- `top_n`: 5
- `include_unavailable`: false
- `ranking_weights`: rate=0.3, score=0.25, recommendation=0.2, reliability=0.15, domain_match=0.1
- `max_rate_eur`: null

**Специфика:**
Если менеджер упоминает жанр, тематику, франшизу или особый навык
(например: JRPG, стихи, Warhammer 40K, аниме, мюзикл) —
извлеки ключевые слова в `specialty_keywords` (массив строк)
и выбери релевантные таблицы из каталога ниже → запиши их ID в `specialty_table_ids`.
Если специфики нет — оба поля оставь пустыми массивами.

**Каталог specialty-таблиц (статический):**
```
DB 216 — жанры игр:
  919: Survival horror        922: SOULS-like
  925: Shoot'em up            951: Battle Royale
  960: JRPG                   972: Colony sim
  973: CCG/ККИ                976: Файтинги
  981: Симуляторы             985: ММОRPG
  986: Гонки                  989: Головоломки
  994: Стратегии              995: МОВА
  996: ММО-шутеры             997: Вампиры/РПГ/хорроры

DB 217 — франшизы/вселенные:
  924: Snoopy/Book of Life    956: Rick & Morty
  959: Monster Hunter         961: Harry Potter
  962: Final Fantasy          963: Family Guy/Walking Dead/American Dad
  964: Eve Online             965: Dune
  967: DnD                   968: Disney/Pixar
  969: Disciples              971: Crash Bandicoot
  974: Blizzard               982: Warhammer
  983: Star Trek/Star Wars    1010: BioShock/Dishonored/Wolfenstein/System Shock/Deus Ex

DB 221 — другие темы:
  946: Стритбол/баскетбол/волейбол/скейтбординг
  958: Ninja Edition          970: Crypto
  977: Техника (корабли/поезда/самолёты)
  979: Стихи                  980: Скандинавская мифология
  984: Футбол                 990: Военные корабли
  991: Боевые искусства       992: Байкерство/мотоциклы
  993: Аниме                  1005: Сервисы (твич/дискорд)
  1013: Азия (культура/традиции)
```

Сгенерируй `request_id` (UUID v4):
```bash
py -c "import uuid; print(uuid.uuid4())"
```

Сохрани JSON во временный файл:
```bash
cat > /tmp/fv_request.json << 'EOF'
{ ... сгенерированный JSON ... }
EOF
```

## Шаг 2: Ранжирование через Baserow

```bash
PYTHONPATH=src py scripts/agent2_rank_baserow.py /tmp/fv_request.json \
  --base-url "$BASEROW_BASE_URL" \
  --token "$BASEROW_API_TOKEN" \
  --vendor-rates-table-id "$BASEROW_VENDOR_RATES_TABLE_ID" \
  --language-vendors-table-id "$BASEROW_LANGUAGE_VENDORS_TABLE_ID" \
  --reliability-form-table-id "$BASEROW_RELIABILITY_FORM_TABLE_ID" \
  > /tmp/fv_agent2.json
```

Прочитай `/tmp/fv_agent2.json` через Read tool.

Если переменные окружения не настроены — объясни пользователю какие нужно задать
(`BASEROW_BASE_URL`, `BASEROW_API_TOKEN`, `BASEROW_VENDOR_RATES_TABLE_ID`,
`BASEROW_LANGUAGE_VENDORS_TABLE_ID`, `BASEROW_RELIABILITY_FORM_TABLE_ID`)
и остановись.

## Шаг 3: LLM-анализ отзывов и специфики

Для каждого кандидата из `top_candidates` прочитай:
- `feedback_summary.highlights`, `feedback_summary.risks`, `feedback_summary.form_comments`
- `important_facts` — важные факты из профиля подрядчика
- `specialty_data` — массив ответов из опросов по тематикам/жанрам/франшизам

Дополнительно загрузи сырые комментарии из Baserow через MCP:
```
mcp__baserow__list_rows(table_id=<BASEROW_RELIABILITY_FORM_TABLE_ID>)
```
Отфильтруй строки по email кандидата (поле `Vendor`).
Поля для анализа: `За что можно похвалить`, `За что можно поругать`,
`Дополнительная информация`.

На основе всех собранных данных сформируй для каждого кандидата:
- **summary** — 1-2 предложения: что говорят менеджеры в целом
- **highlights_llm** — 2-3 сильных стороны
- **risks_llm** — риски (если есть)
- **sentiment** — positive / neutral / negative
- **specialty_match** — если менеджер указал специфику (specialty_keywords непустой):
  проверь `specialty_data` и `important_facts` — есть ли у кандидата
  релевантный опыт? Напиши 1-2 предложения с конкретными деталями из ответов.
  Если данных нет — пиши «Данных о специфике нет».

Правила: опирайся только на реальные данные. Если отзывов нет — пиши
«Отзывов нет». Не придумывай.

## Шаг 4: Вывод результатов в чате

Отформатируй и выведи результаты в Markdown:

```
## Результаты поиска: {source} → {target}, {type}{, до X EUR}

Найдено кандидатов: **N**
{Отсеяно M: причины}

---

### 1. {Имя} — {match_score}%

| | |
|---|---|
| **Email** | ... |
| **Ставка** | ... EUR |
| **Оценка** | ... |
| **Рекомендация** | ... |
| **Надёжность** | ... |
| **Статус** | ... |
| **Часовой пояс** | ... |
| **Mattermost** | да/нет |
| **Домены** | ... |
| **CAT** | ... |
| **Важные факты** | ... (если есть) |

**Отзывы менеджеров:** {summary}
- Хвалят: {highlights_llm}
- Риски: {risks_llm}
- Специфика: {specialty_match} (если менеджер запрашивал специфику)
```

Не отправляй в Mattermost — только показывай в чате.
Сохрани финальный agent2 output в `/tmp/fv_agent2.json` для возможного
последующего использования.
