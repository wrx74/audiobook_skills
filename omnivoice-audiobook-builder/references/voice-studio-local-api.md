# VoiceStudio local API and renderer

Read this reference when generating or debugging OmniVoice output through VoiceStudio.

## Proven local configuration

| Field | Value |
|---|---|
| API | `http://127.0.0.1:3900` |
| Health | `GET /health` |
| Generate | `POST /generate` multipart form |
| Engine | `omnivoice` |
| Language | `ru` |
| Steps | `48` |
| Seed | `42` |
| Speed | `1.0` |
| Chunking | `max_chunk_chars=0`, `crossfade_ms=0` |
| Output | PCM WAV, 48 kHz mono |
| Loudness | `loudnorm=I=-19:TP=-2:LRA=11` |

The endpoint may differ if VoiceStudio is configured with another port. Query `/health` rather than assuming the service is running.

## Manifest

```json
[
  {
    "text": "Первая смысловая часть.",
    "mood": "reflective, restrained",
    "pause": 650
  },
  {
    "text": "— Следующая реплика?",
    "mood": "wary curiosity",
    "pause": 300
  },
  {
    "text": "Финальная строка.",
    "pause": 0
  }
]
```

`mood` documents editorial intent; the renderer does not speak it or claim the engine applied it. `pause` becomes `[pause Nms]`, which VoiceStudio renders as silence between spans while reusing one cached reference.

## Renderer

```powershell
python scripts/render_omnivoice.py `
  --manifest "C:\work\scene.json" `
  --source "C:\work\source.txt" `
  --reference-audio "C:\work\voice.wav" `
  --reference-text-file "C:\work\voice.txt" `
  --output "C:\work\scene-directed.wav"
```

Use `--dry-run` to validate the manifest and reference identity without calling VoiceStudio. Existing outputs are protected; pass `--overwrite` only when replacement is intended.

The report is written beside the WAV as `*.verification.json` unless `--report` is supplied. It records effective settings, reference and output SHA-256, pauses, duration, codec, rate, channels, health response, and full-decode status.

## Direct API fields

The script sends `text`, `language`, `ref_audio`, `ref_text`, `num_step`, `guidance_scale`, `speed`, `seed`, `engine`, `max_chunk_chars`, and `crossfade_ms` as multipart fields. A reference clip and matching transcript switch OmniVoice from voice design to clone conditioning.

## Recovery

- HTTP failure: read the returned body and VoiceStudio log; do not replace clone conditioning with voice design silently.
- Timbre changes: verify all spans share the same reference bytes and transcript. Check the report's reference hash.
- Missing words: compare normalized source and manifest, then inspect dropped-text response headers or logs.
- Slow or distorted long take: divide into section manifests, not independent voices; retain the same reference identity and verify each section before assembly.