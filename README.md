# AI Personal Operational System — POS {sprint}

Batch: sprint-X26

2 марта — 14 марта 2026

Материалы, правила и конфигурации участников спринта — промпты, skills, CLAUDE.md и другие артефакты Personal Operational System.

## Practice

Общие гайды и практики спринта.

| Гайд | Описание |
|------|----------|
| [Naming Convention & Vault Structure](practice/naming-convention-vault-structure.md) | Формула имён файлов, структура Obsidian vault, теги, YAML frontmatter, интеграция с AI-агентами. [Веб-версия](https://pos-pipelines.netlify.app/naming.html) |
| [Правила оркестрации моделей](practice/sergey-zinenko-orchestration-rules.md) | Таблица делегирования Opus/Sonnet/Haiku, автоэскалация, правила сессии |
| [deck — HTML Presentation Generator](skills/deck) | Скилл для Claude Code: генерация single-file HTML презентаций. 2 стиля (terminal / editorial), готовые компоненты, примеры |
| [CLI Awareness System](practice/cli-awareness-system) | Status Line, Footer Protocol, Task Awareness, Mission Control — 4 уровня информационного слоя в терминале Claude Code. Скрипты, шаблоны, примеры настройки |

## Skills

Скиллы участников спринта для Claude Code.

### [@khabaroff](https://github.com/khabaroff)

| Скилл | Описание |
|-------|----------|
| [business-analyst-toolkit](skills/business-analyst-toolkit) | Анализ бизнес-процессов, документация требований, оптимизация workflow |
| [markdown-new](skills/markdown-new) | Конвертация веб-страниц в Markdown через markdown.new для AI-воркфлоу |
| [product-strategist](skills/product-strategist) | Продуктовая стратегия — OKR, анализ рынка, vision, масштабирование команды |
| [seo-strategist](skills/seo-strategist) | SEO-стратегия — аудит, семантика, контент-план, техническая оптимизация |
| [writing-content](skills/writing-content) | Написание текстов для вайб-маркетинга по Julian Shapiro framework |

### [@gohardstronger](https://github.com/gohardstronger)

| Скилл | Описание |
|-------|----------|
| [daily-work](skills/daily-work) | Автоматический дневной отчёт из activity log, git, session checkpoints в Obsidian |
| [tg-saved](skills/tg-saved) | Telegram Saved Messages → глубокий анализ через Claude → Obsidian |
| [yt-transcribe](skills/yt-transcribe) | Транскрибация YouTube через mlx-whisper (Apple Silicon) → Obsidian |

### [@fmbo31](https://github.com/fmbo31)

| Скилл | Описание |
|-------|----------|
| [find-vendor](skills/find-vendor) | Оркестратор поиска подрядчика — NL-запрос, фильтрация и ранжирование из Baserow |
| [summarize-comments](skills/summarize-comments) | LLM-выжимка из комментариев менеджеров о подрядчиках |

### [@alexfrmn](https://github.com/alexfrmn)

| Скилл | Описание |
|-------|----------|
| [session-management](skills/session-management) | Управление контекстом сессии — start, save, compress, continue |

### [@usatovw](https://github.com/usatovw)

| Скилл | Описание |
|-------|----------|
| [skill-security](skills/skill-security) | 7-томный security-аудит и ребилд скиллов Claude Code |

### [@valeryvpetrov-dev](https://github.com/valeryvpetrov-dev)

| Скилл | Описание |
|-------|----------|
| [learning-loop](skills/learning-loop) | Обновление раздела Learning Loop в markdown-файле POS — фиксация понимания, задач и ссылок |

### [@divnomorskoe1989](https://github.com/divnomorskoe1989)

| Скилл | Описание |
|-------|----------|
| [jira-monitor](skills/jira-monitor) | Kanban-мониторинг Jira — метрики потока, поиск bottleneck, дефекты, sprint scope, оценки |

### [@sergeyryumkin](https://github.com/sergeyryumkin)

| Скилл | Описание |
|-------|----------|
| [student-agent-os](skills/sergeiriumkin/student-agent-os.skill) | Автоматизация общения со студентами — агентная ОС |
| [telegram-faq-bot](skills/sergeiriumkin/telegram-faq-bot.skill) | Telegram FAQ-бот для студентов |

### [@sbg075](https://github.com/sbg075)

| Скилл | Описание |
|-------|----------|
| [ai-bear-newsletter](skills/ai-bear-newsletter) | AI-Bear newsletter — трансформация Notion-черновиков в статьи для LinkedIn/Substack |

### [@zariavv](https://github.com/zariavv)

| Скилл | Описание |
|-------|----------|
| [project-knowledge-base](skills/project-knowledge-base) | Инициализация и обновление базы знаний проекта (PKB.md) в Obsidian — агрегация из Google Drive, Gmail, Telegram, moo.team и локальных заметок |

### [@bykovvasily](https://github.com/bykovvasily)

| Скилл | Описание |
|-------|----------|
| [roi-razvitie-draft](skills/roi-razvitie-draft) | Драфт документа к еженедельной встрече «Roi Развитие» (среда) — пункты для обсуждения и заметки |

### [@aPoWall](https://github.com/aPoWall)

| Скилл | Описание |
|-------|----------|
| [deck](skills/deck) | HTML-генератор презентаций — 2 стиля (terminal/editorial), single-file, zero dependencies |

## Chrome Extensions

Расширения для браузера Chrome, созданные участниками спринта.

| Расширение | Автор | Описание |
|------------|-------|----------|
| [ev_garde](Chrome%20Extensions/ev_garde) | [@ev_garde](https://github.com/ev_garde) | Chrome-расширение new tab + скилл ai-bear-newsletter |

## Участие

Добавляйте свои материалы через PR.

Формат имени файла: `имя-фамилия-тема.md`
