# /tg-saved v2 — Telegram Saved Messages → Deep Analysis → Obsidian

## Назначение

Скилл извлекает сообщения из Telegram "Избранное" (Saved Messages) за последние N дней, автоматически парсит контент всех ссылок в сообщениях (requests + BeautifulSoup, до 5000 символов на URL), затем для каждого сообщения запускает глубокий анализ через Claude CLI subprocess (модель Sonnet). Результат — подробная структурированная заметка в Obsidian `00-inbox/` с YAML frontmatter, секциями анализа, ссылками и оригинальным текстом. Поддерживает **дедупликацию** — при повторном запуске обрабатывает только новые сообщения.

## Какую боль закрывает

- **Информационный завал**: Telegram Saved Messages копятся, но никогда не перечитываются. Ценные ссылки и находки теряются.
- **Ручная обработка**: Каждую ссылку нужно открыть, прочитать, законспектировать — на 30 сообщений это 2-3 часа.
- **Нет структуры**: Saved Messages — это свалка без тегов, категорий и поиска.
- **Скилл превращает хаос в структурированную базу знаний** — автоматически, за минуты.

## Компоненты

| Файл | Назначение |
|------|-----------|
| `scripts/tg_saved_extract.py` | Python-скрипт: Telethon для извлечения сообщений + requests/BeautifulSoup для парсинга URL + дедупликация |
| `requirements.txt` | Зависимости: telethon, requests, beautifulsoup4 |
| `tg-saved.md` | Claude Code команда: оркестрация (запуск скрипта → анализ через claude CLI → создание заметок) |

## Пайплайн

```
/tg-saved [N дней] [--all]
    ↓
1. Python-скрипт (Telethon):
   - Подключается к Telegram API (session file, без повторной авторизации)
   - Читает Saved Messages за последние N дней
   - Загружает processed_ids.json → фильтрует уже обработанные (если не --all)
   - Для каждого сообщения: извлекает текст, media_type, forward_from, URLs
   - Для webpage-сообщений: добавляет webpage_title, webpage_description
    ↓
2. URL fetching (requests + BeautifulSoup, 4 потока параллельно):
   - Для каждого уникального URL: GET с таймаутом 10с
   - HTML-парсинг: удаляет script/style/nav/footer/header/aside
   - Берёт контент из article → main → body (fallback chain)
   - Обрезает до 5000 символов
    ↓
3. Сохраняет JSON в /tmp/tg_saved_output.json
    ↓
4. Claude Code читает JSON, фильтрует low-value сообщения
    ↓
5. Субагенты параллельно (3-4 штуки):
   - echo JSON | claude -p --model sonnet
   - Claude Sonnet анализирует сообщение + спарсенный контент URL
   - Возвращает YAML frontmatter + секции анализа
    ↓
6. Создание MD-файлов в Obsidian 00-inbox/
    ↓
7. --mark-processed: обновляет processed_ids.json
```

## Использование

```bash
/tg-saved          # последние 30 дней, только новые
/tg-saved 7        # последние 7 дней, только новые
/tg-saved --all    # последние 30 дней, повторно обработать ВСЕ
/tg-saved 7 --all  # последние 7 дней, повторно обработать ВСЕ
```

## Зависимости

| Пакет | Версия | Назначение |
|-------|--------|-----------|
| telethon | 1.42.0 | Telegram API client |
| requests | >=2.31.0 | HTTP-запросы для парсинга URL |
| beautifulsoup4 | >=4.12.0 | HTML-парсинг страниц |
| `claude` CLI | latest | Subprocess для deep analysis (модель Sonnet) |

## Настройка

1. Получить `API_ID` и `API_HASH` на https://my.telegram.org
2. Задать переменные окружения `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`
3. Создать venv и установить зависимости: `pip install -r requirements.txt`
4. Первый запуск — в интерактивном терминале для OTP-авторизации:
   ```bash
   python3 scripts/tg_saved_extract.py
   ```
5. Дальше session file сохраняется и повторная авторизация не нужна

## Формат выходной заметки

```
{personal} {type} описание – YYYY-MM-DD – Claude Code.md
```

Секции: Что это → Ключевые возможности → Инсайты → Сильные стороны → Слабые стороны → Вердикт → Ссылки → Оригинал
