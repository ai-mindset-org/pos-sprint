# YT Transcribe — YouTube → Whisper → Obsidian

Транскрибирует YouTube-видео через mlx-whisper (Apple Silicon, Metal-native) с параллельными чанками.
Fallback на openai-whisper если mlx недоступен.

## Какую боль закрывает

- **Потерянный контент видео**: Посмотрел лекцию/подкаст — через неделю забыл 90%. Нет текстовой базы для поиска.
- **Нет транскриптов для русского**: YouTube auto-captions для русского языка — мусор. Whisper даёт quality транскрипцию.
- **Ручная обработка**: Переслушивать 2-часовую лекцию чтобы найти один момент — боль.
- **Скилл превращает видео в searchable knowledge base** — транскрипт + саммери + привязка слайдов, всё в Obsidian.

## Пайплайн

```
/yt-transcribe <YouTube URL>
    ↓
1. yt-dlp скачивает аудио (WAV 16kHz mono)
    ↓
2. Длинные видео (>20 мин) → ffmpeg split на чанки по 20 мин
    ↓
3. mlx-whisper (large-v3) транскрибирует чанки параллельно (до 4 воркеров)
    ↓
4. Merge сегментов с offset timestamps, сортировка по времени
    ↓
5. Claude обрабатывает: форматирует секции, привязывает слайды
    ↓
6. Два файла в Obsidian:
   - {transcript} — полный текст с [MM:SS] таймкодами
   - {summary} — подробное саммери, самодостаточный артефакт
   - (опционально) {slides} — презентация с PNG слайдами
```

## Движки

| Движок | Платформа | Скорость | Примечание |
|--------|-----------|----------|------------|
| **mlx-whisper** (default) | Apple Silicon | ~8-10x vs openai | Metal-native, оптимален для Mac |
| openai-whisper (fallback) | Любая | 1x (базовая) | Универсальный |

Auto-detect: если `mlx-whisper` установлен — используется он, иначе `openai-whisper`.

## Использование

```bash
/yt-transcribe <YouTube URL>
```

Скрипт напрямую:
```bash
python3 scripts/yt_transcribe.py \
  --url "https://youtube.com/watch?v=..." \
  --model large-v3 \
  --engine auto \
  --max-workers 4 \
  --output /tmp
```

### Аргументы
- `--url` — YouTube URL (обязательный)
- `--model` — Whisper model (default: `large-v3`). Для скорости: `medium`
- `--engine` — `auto` | `mlx` | `openai` (default: `auto`)
- `--chunk-duration` — длина чанка в секундах (default: `1200` = 20 мин)
- `--max-workers` — макс. параллельных воркеров (default: `4`)
- `--output` — директория для .md (default: `/tmp`)

## Зависимости

- **ffmpeg** — `brew install ffmpeg`
- **yt-dlp** — скачивание аудио
- **mlx-whisper** — транскрипция (Apple Silicon, Metal)
- **openai-whisper** — fallback транскрипция
- **python-pptx** — чтение PPTX презентаций
- **poppler** — `brew install poppler` (PDF → PNG)

## Модели Whisper

| Модель    | Скорость (mlx) | Качество | Когда использовать |
|-----------|----------------|----------|--------------------|
| medium    | Очень быстрая  | Хорошее  | Одноязычное видео, нужна скорость |
| large-v3  | Быстрая        | Лучшее   | Микс ru/en, сложная терминология |

## Формат выхода

Всегда создаёт 2 файла:
1. **Транскрипт**: `{проект} {transcript} описание – YYYY-MM-DD – Claude Code.md`
2. **Саммери**: `{проект} {summary} описание – YYYY-MM-DD – Claude Code.md`
3. (Опционально) **Слайды**: `{проект} {slides} PREFIX Презентация – YYYY-MM-DD – Claude Code.md`
