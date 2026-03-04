#!/usr/bin/env python3
"""YouTube video transcription via yt-dlp + mlx-whisper with parallel chunking.

Optimized for Apple Silicon — uses mlx-whisper (Metal-native) instead of openai-whisper.
Falls back to openai-whisper if mlx-whisper is not available.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import yt_dlp

# Chunk duration in seconds (20 min)
CHUNK_DURATION = 20 * 60
# Max parallel workers
MAX_WORKERS = 4


def format_timestamp(seconds: float) -> str:
    """Format seconds to [MM:SS] or [H:MM:SS] for long videos."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"[{h}:{m:02d}:{s:02d}]"
    return f"[{m:02d}:{s:02d}]"


def format_duration(seconds: float) -> str:
    """Format seconds to human-readable duration."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def get_video_metadata(url: str) -> dict:
    """Extract video metadata via yt-dlp without downloading."""
    print(f"Extracting metadata for: {url}")
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        data = ydl.extract_info(url, download=False)
    return {
        "title": data.get("title", "Unknown"),
        "duration": data.get("duration", 0),
        "channel": data.get("channel", data.get("uploader", "Unknown")),
        "upload_date": data.get("upload_date", ""),
        "description": data.get("description", ""),
    }


def download_audio(url: str, output_dir: str) -> str:
    """Download audio from YouTube as WAV 16kHz mono. Returns actual file path."""
    print("Downloading audio...")
    outtmpl = os.path.join(output_dir, "audio.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }],
        "postprocessor_args": {
            "ffmpeg": ["-ar", "16000", "-ac", "1"],
        },
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    wav_path = os.path.join(output_dir, "audio.wav")
    if not os.path.exists(wav_path):
        for f in os.listdir(output_dir):
            if f.startswith("audio"):
                wav_path = os.path.join(output_dir, f)
                break
    return wav_path


def split_audio(audio_path: str, output_dir: str, chunk_duration: int) -> list[tuple[str, float]]:
    """Split audio into chunks using ffmpeg. Returns list of (chunk_path, offset_seconds)."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "json", audio_path],
        capture_output=True, text=True, check=True,
    )
    total_duration = float(json.loads(result.stdout)["format"]["duration"])

    chunks = []
    offset = 0.0
    idx = 0
    while offset < total_duration:
        chunk_path = os.path.join(output_dir, f"chunk_{idx:03d}.wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path,
             "-ss", str(offset),
             "-t", str(chunk_duration),
             "-ar", "16000", "-ac", "1",
             "-loglevel", "error",
             chunk_path],
            check=True,
        )
        chunks.append((chunk_path, offset))
        offset += chunk_duration
        idx += 1

    print(f"Split into {len(chunks)} chunks ({chunk_duration // 60} min each)")
    return chunks


def transcribe_chunk_mlx(chunk_path: str, offset: float, model_name: str, chunk_idx: int) -> list[dict]:
    """Transcribe a single audio chunk using mlx-whisper. Runs in a separate process."""
    import mlx_whisper

    print(f"  [Chunk {chunk_idx}] Starting mlx-whisper transcription (offset {format_timestamp(offset)})...")
    result = mlx_whisper.transcribe(
        chunk_path,
        path_or_hf_repo=f"mlx-community/whisper-{model_name}-mlx",
        verbose=False,
    )

    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": seg["start"] + offset,
            "end": seg["end"] + offset,
            "text": seg["text"],
        })

    print(f"  [Chunk {chunk_idx}] Done — {len(segments)} segments")
    return segments


def transcribe_chunk_openai(chunk_path: str, offset: float, model_name: str, chunk_idx: int) -> list[dict]:
    """Transcribe a single audio chunk using openai-whisper (fallback). Runs in a separate process."""
    import whisper

    print(f"  [Chunk {chunk_idx}] Starting openai-whisper transcription (offset {format_timestamp(offset)})...")
    model = whisper.load_model(model_name)
    result = model.transcribe(
        chunk_path,
        language=None,
        verbose=False,
    )

    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": seg["start"] + offset,
            "end": seg["end"] + offset,
            "text": seg["text"],
        })

    print(f"  [Chunk {chunk_idx}] Done — {len(segments)} segments")
    return segments


def detect_engine() -> str:
    """Detect best available transcription engine."""
    try:
        import mlx_whisper  # noqa: F401
        return "mlx"
    except ImportError:
        pass
    try:
        import whisper  # noqa: F401
        return "openai"
    except ImportError:
        pass
    print("ERROR: No whisper engine found. Install mlx-whisper or openai-whisper.", file=sys.stderr)
    sys.exit(1)


def transcribe_parallel(chunks: list[tuple[str, float]], model_name: str, max_workers: int, engine: str) -> list[dict]:
    """Transcribe all chunks in parallel, merge results sorted by time."""
    all_segments = []
    transcribe_fn = transcribe_chunk_mlx if engine == "mlx" else transcribe_chunk_openai

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for idx, (chunk_path, offset) in enumerate(chunks):
            future = executor.submit(transcribe_fn, chunk_path, offset, model_name, idx)
            futures[future] = idx

        for future in as_completed(futures):
            idx = futures[future]
            try:
                segments = future.result()
                all_segments.extend(segments)
            except Exception as e:
                print(f"  [Chunk {idx}] ERROR: {e}", file=sys.stderr)

    all_segments.sort(key=lambda s: s["start"])
    return all_segments


def transcribe_single(audio_path: str, model_name: str, engine: str) -> list[dict]:
    """Transcribe a single audio file (short videos, no chunking)."""
    if engine == "mlx":
        import mlx_whisper
        print(f"Transcribing with mlx-whisper ({model_name})...")
        result = mlx_whisper.transcribe(
            audio_path,
            path_or_hf_repo=f"mlx-community/whisper-{model_name}-mlx",
            verbose=False,
        )
    else:
        import whisper
        print(f"Transcribing with openai-whisper ({model_name})...")
        model = whisper.load_model(model_name)
        result = model.transcribe(audio_path, language=None, verbose=False)

    print(f"Detected language: {result.get('language', 'unknown')}")
    return result["segments"]


def segments_to_markdown(
    segments: list[dict],
    metadata: dict,
    url: str,
    engine: str,
) -> str:
    """Convert Whisper segments to Markdown with frontmatter and timestamps."""
    title = metadata["title"]
    duration = format_duration(metadata["duration"])
    channel = metadata["channel"]
    date_now = datetime.now().strftime("%Y-%m-%d")

    lines = [
        "---",
        f"title: \"{title}\"",
        f"source: youtube",
        f"url: \"{url}\"",
        f"channel: \"{channel}\"",
        f"duration: \"{duration}\"",
        f"date: {date_now}",
        f"type: transcript",
        f"engine: {engine}",
        f"status: raw",
        "---",
        "",
        f"# {title}",
        "",
        f"**Channel:** {channel}  ",
        f"**Duration:** {duration}  ",
        f"**URL:** {url}  ",
        f"**Engine:** {engine}-whisper",
        "",
        "---",
        "",
        "## Transcript",
        "",
    ]

    for seg in segments:
        ts = format_timestamp(seg["start"])
        text = seg["text"].strip()
        lines.append(f"{ts} {text}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Transcribe YouTube video via mlx-whisper / openai-whisper")
    parser.add_argument("--url", required=True, help="YouTube video URL")
    parser.add_argument("--model", default="large-v3", help="Whisper model (default: large-v3)")
    parser.add_argument("--output", default="/tmp", help="Output directory for .md (default: /tmp)")
    parser.add_argument("--engine", choices=["mlx", "openai", "auto"], default="auto",
                        help="Transcription engine (default: auto — prefers mlx)")
    parser.add_argument("--chunk-duration", type=int, default=CHUNK_DURATION,
                        help=f"Chunk duration in seconds (default: {CHUNK_DURATION})")
    parser.add_argument("--max-workers", type=int, default=MAX_WORKERS,
                        help=f"Max parallel workers (default: {MAX_WORKERS})")
    args = parser.parse_args()

    # Detect engine
    if args.engine == "auto":
        engine = detect_engine()
    else:
        engine = args.engine
    print(f"Engine: {engine}-whisper")

    # 1. Get metadata
    metadata = get_video_metadata(args.url)
    duration_sec = metadata["duration"]
    print(f"Title: {metadata['title']}")
    print(f"Duration: {format_duration(duration_sec)}")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 2. Download audio
        audio_path = download_audio(args.url, tmpdir)
        print(f"Audio saved to: {audio_path}")

        # 3. Decide: parallel chunks or single transcription
        if duration_sec > args.chunk_duration:
            chunks_dir = os.path.join(tmpdir, "chunks")
            os.makedirs(chunks_dir)
            chunks = split_audio(audio_path, chunks_dir, args.chunk_duration)
            print(f"Transcribing {len(chunks)} chunks in parallel (max {args.max_workers} workers)...")
            segments = transcribe_parallel(chunks, args.model, args.max_workers, engine)
        else:
            segments = transcribe_single(audio_path, args.model, engine)

    # 4. Generate markdown
    md_content = segments_to_markdown(segments, metadata, args.url, engine)

    # 5. Save .md
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in metadata["title"])[:80].strip()
    output_filename = f"YT Transcript {safe_title}.md"
    output_path = os.path.join(args.output, output_filename)

    Path(args.output).mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\nTranscript saved to: {output_path}")
    print(f"Segments: {len(segments)}")
    print(f"Engine: {engine}-whisper")


if __name__ == "__main__":
    main()
