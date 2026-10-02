#!/usr/bin/env python3
"""Render a verified OmniVoice take through a local VoiceStudio API."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request

DEFAULT_API_URL = "http://127.0.0.1:3900"
DEFAULT_STEPS = 48
DEFAULT_SEED = 42
DEFAULT_SPEED = 1.0
DEFAULT_SAMPLE_RATE = 48000
DEFAULT_LOUDNESS = "I=-19:TP=-2:LRA=11"
PAUSE_RE = re.compile(r"\[\s*pause\s+\d+ms\s*\]", re.IGNORECASE)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalized_spoken_text(text: str) -> str:
    return normalize_text(PAUSE_RE.sub(" ", text))


def render_manifest_text(manifest: list[dict]) -> str:
    if not isinstance(manifest, list) or not manifest:
        raise ValueError("Manifest must be a non-empty JSON array")
    lines: list[str] = []
    for index, segment in enumerate(manifest, start=1):
        if not isinstance(segment, dict):
            raise ValueError(f"Segment {index} must be an object")
        text = str(segment.get("text", "")).strip()
        if not text:
            raise ValueError(f"Segment {index} has empty text")
        pause = segment.get("pause", segment.get("pause_ms", 0))
        if isinstance(pause, bool) or not isinstance(pause, (int, float)):
            raise ValueError(f"Segment {index} pause must be numeric")
        pause_ms = int(pause)
        if pause_ms < 0 or pause_ms > 10000:
            raise ValueError(f"Segment {index} pause must be between 0 and 10000 ms")
        lines.append(text)
        if pause_ms:
            lines.append(f"[pause {pause_ms}ms]")
    return "\n".join(lines)


def base_report(*, reference_audio: str, reference_sha256: str, steps: int,
                seed: int, speed: float, pauses: list[int]) -> dict:
    return {
        "engine": "OmniVoice",
        "mode": "clone from one fixed reference",
        "reference_audio": reference_audio,
        "reference_sha256": reference_sha256,
        "steps": steps,
        "seed": seed,
        "speed": speed,
        "pauses_ms": pauses,
    }


def run(command: list[str], *, label: str) -> None:
    completed = subprocess.run(command, check=False)
    if completed.returncode:
        raise RuntimeError(f"{label} failed with exit code {completed.returncode}")


def require_tool(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise RuntimeError(f"Required executable not found: {name}")
    return found


def check_health(api_url: str) -> dict:
    with urllib.request.urlopen(f"{api_url.rstrip('/')}/health", timeout=10) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("status") != "ok":
        raise RuntimeError(f"VoiceStudio health check failed: {result}")
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=pathlib.Path,
                        help="JSON array of {text, pause|pause_ms} segments")
    parser.add_argument("--reference-audio", required=True, type=pathlib.Path)
    parser.add_argument("--reference-text-file", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--source", type=pathlib.Path,
                        help="Optional original text for normalized identity verification")
    parser.add_argument("--report", type=pathlib.Path)
    parser.add_argument("--build-dir", type=pathlib.Path)
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--language", default="ru")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--speed", type=float, default=DEFAULT_SPEED)
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--loudness", default=DEFAULT_LOUDNESS)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    for path in (args.manifest, args.reference_audio, args.reference_text_file):
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.source and not args.source.is_file():
        raise FileNotFoundError(args.source)
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"Output exists; pass --overwrite: {args.output}")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    synthesis_text = render_manifest_text(manifest)
    pauses = [int(s.get("pause", s.get("pause_ms", 0))) for s in manifest if int(s.get("pause", s.get("pause_ms", 0))) > 0]
    spoken = normalized_spoken_text(synthesis_text)
    source_identical = None
    if args.source:
        source_identical = normalize_text(args.source.read_text(encoding="utf-8-sig")) == spoken
        if not source_identical:
            raise ValueError("Manifest spoken text differs from --source")

    report = base_report(
        reference_audio=str(args.reference_audio.resolve()),
        reference_sha256=sha256(args.reference_audio),
        steps=args.steps,
        seed=args.seed,
        speed=args.speed,
        pauses=pauses,
    )
    report.update({
        "segments": len(manifest),
        "spoken_text_sha256": hashlib.sha256(spoken.encode("utf-8")).hexdigest().upper(),
        "spoken_text_identical_to_source": source_identical,
        "sample_rate": args.sample_rate,
        "loudness_filter": args.loudness,
    })
    if args.dry_run:
        report["ok"] = True
        report["dry_run"] = True
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    curl = require_tool("curl.exe" if sys.platform == "win32" else "curl")
    ffmpeg = require_tool("ffmpeg")
    ffprobe = require_tool("ffprobe")
    health = check_health(args.api_url)

    build_dir = args.build_dir or args.output.parent / f".{args.output.stem}-build"
    build_dir.mkdir(parents=True, exist_ok=True)
    synthesis_path = build_dir / "synthesis-with-pauses.txt"
    synthesis_path.write_text(synthesis_text, encoding="utf-8")
    raw_path = build_dir / "raw.wav"

    generate = [
        curl, "-sS", "--fail-with-body", "-X", "POST",
        f"{args.api_url.rstrip('/')}/generate",
        "-F", f"text=<{synthesis_path}",
        "-F", f"language={args.language}",
        "-F", f"ref_audio=@{args.reference_audio};type=audio/wav",
        "-F", f"ref_text=<{args.reference_text_file}",
        "-F", f"num_step={args.steps}",
        "-F", "guidance_scale=2.0",
        "-F", f"speed={args.speed}",
        "-F", f"seed={args.seed}",
        "-F", "engine=omnivoice",
        "-F", "max_chunk_chars=0",
        "-F", "crossfade_ms=0",
        "-o", str(raw_path),
    ]
    run(generate, label="VoiceStudio generation")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    run([
        ffmpeg, "-y", "-v", "error", "-i", str(raw_path),
        "-af", f"loudnorm={args.loudness}", "-ar", str(args.sample_rate),
        "-ac", "1", "-c:a", "pcm_s16le", str(args.output),
    ], label="audio normalization")
    run([ffmpeg, "-v", "error", "-i", str(args.output), "-f", "null",
         "NUL" if sys.platform == "win32" else "/dev/null"], label="full decode")

    probe = subprocess.run([
        ffprobe, "-v", "error", "-show_entries", "format=duration,size",
        "-show_entries", "stream=codec_name,sample_rate,channels",
        "-of", "json", str(args.output),
    ], check=True, capture_output=True, text=True, encoding="utf-8")
    media = json.loads(probe.stdout)
    stream = media["streams"][0]
    report.update({
        "ok": True,
        "dry_run": False,
        "voice_studio_health": health,
        "output": str(args.output.resolve()),
        "output_sha256": sha256(args.output),
        "duration_seconds": round(float(media["format"]["duration"]), 3),
        "size_bytes": int(media["format"]["size"]),
        "codec": stream["codec_name"],
        "sample_rate": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "full_decode": "passed",
    })
    report_path = args.report or args.output.with_suffix(".verification.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())