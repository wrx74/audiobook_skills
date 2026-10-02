---
name: silero-audiobook-builder
description: Use when converting Russian text or FB2 into Silero speech, from short pronunciation samples to resumable long-form audiobooks with pronunciation control, verified media, section MP3 files, or chapterized M4B output.
---

# Silero Audiobook Builder

## Overview

Build Russian Silero speech with a verified local pipeline. Preserve inputs, approve the voice on a short sample before long-form work, cache audiobook synthesis by content, and treat media verification as part of every build.

## Choose the build mode

- **Short TTS test:** For pasted text, a tongue twister, or a pronunciation check, synthesize the complete text as the sample. Preserve the original and a separate prepared synthesis text, use an existing tested sample entry point such as `tools/run_silero.py`, and produce a verified WAV. Do not require book sections, MP3 masters, M4B chapters, or a separate pre-approval sample.
- **Audiobook:** Follow the full resumable workflow below, including the representative listening sample, manifest, content-addressed cache, section masters, chapterized M4B, and protected-file checks.

## Required workflow

1. Locate the exact source and an existing Silero entry point. Search the current repository, registered Git worktrees, saved project locations, and project documentation before concluding it is absent. Prefer `tools/build_silero_audiobook.py` for books and an existing tested sample runner for short tests; inspect `--help` and tests. Never invent a script or unsupported flag.
2. Record SHA-256 and size for the source and any protected comparison samples. Create a separate build root; never write beside or over the source.
3. Run preflight: parse the source, report logical section order when applicable and visible character count, verify free space, `ffmpeg`, `ffprobe`, the chosen Silero model/speaker, PyTorch CUDA, and the NVIDIA device. Before installing dependencies, inspect project docs and known environments for an existing Python executable and model cache, then verify imports and CUDA with that exact interpreter. For a CUDA-required job, fail instead of silently using CPU.
4. Unless the user already approved this exact model, speaker, and preparation profile, synthesize a representative 2–3 minute sample and wait for listening approval before the full book.
5. Build with a manifest and content-addressed WAV cache. Re-running the identical command must reuse only identity-matching, `ffprobe`-valid fragments. Do not delete the cache or use destructive overwrite during recovery.
6. Create normalized section MP3 masters and one chapterized M4B. Write temporary siblings, validate, then atomically replace final paths.
7. Require `logs/verification.json` with `"ok": true`, then recompute protected hashes. Report objective evidence separately from the user's subjective listening check.

For a short TTS test, apply steps 1–3 and 7, synthesize the supplied text, and verify the WAV by `ffprobe` plus a full decode. Record source, prepared-text, and audio hashes; codec, sample rate, channels, duration, model, speaker, and device. Present the audio for listening and ask the user to judge pronunciation, stress, pacing, pauses, and artifacts.

For Russian preparation and FB2/TXT rules, read [references/russian-text-preparation.md](references/russian-text-preparation.md). For acceptance checks, read [references/verification-checklist.md](references/verification-checklist.md).

When the user wants a warmer, denser final sound or accepts that mastering profile on a sample, read [references/mastering.md](references/mastering.md). Keep the unmastered master, apply processing only after section or sample assembly, and do not describe mastering as a remedy for flat prosody.

## Efficient long-form finalization

For an audiobook, make the production path explicit before launching long jobs:

1. Reuse every identity-matching validated PCM cache fragment; do not resynthesize unchanged speech for mastering-only work.
2. Assemble and protect each unmastered section WAV once, then apply the approved section mastering profile once.
3. When final loudness or true-peak compliance must survive MP3/AAC encoding, use codec-aware two-pass loudness normalization from the start: measure the complete ordered input in pass 1, record the measured values, and use those exact values with conservative codec headroom in pass 2. Do not tune true peak through repeated full-book trial encodes.
4. Encode one candidate chapterized M4B, then perform one full decode with measured integrated loudness, LRA, and true peak. If it fails, diagnose the cause and choose a deterministic correction before allowing another full encode.
5. Keep long local media jobs in one running process. Use compact status polling and bounded log tails; never inject full source fragments, manifests, file inventories, or repetitive unchanged progress into model context. Report meaningful milestones and failures, not every unchanged poll.

Treat local media runtime and model usage separately: `ffmpeg` compute time does not itself require model reasoning, but every tool round trip, large output, and progress message expands the agent session. Prefer quiet waits and machine-readable logs.
## Proven default profile

| Setting | Default |
|---|---|
| Model / speaker | `v5_5_ru` / `xenia` |
| Device | CUDA only |
| Audio | 48 kHz, mono |
| Silero flags | stress, homograph stress, `ё`, homograph `ё`, single-vowel stress |
| Pauses | 180 ms sentence; 650 ms paragraph |
| Chapter titles | Explicit 1000 ms silence before the spoken title and 1000 ms after it; make both values configurable and include them in the manifest and cache identity |
| Fragments | roughly 5–10 minutes, composed of model-safe units no longer than 800 characters |
| Section masters | MP3, 48 kHz mono, 128 kbit/s, section-level loudness normalization |
| Book | AAC M4B with section chapters |

Change defaults when the user selects another tested voice or model; include every effective setting in fragment identity.

## Existing pipeline example

```powershell
python tools/build_silero_audiobook.py `
  --source "E:\Audio_books\Input\book.fb2" `
  --build-root "E:\Audio_books\Output\book"
```

Run the same command after interruption. Use `--limit-sections 1` with a distinct smoke-test build root when a short structural test is useful.

## Common mistakes

- Treating FB2 XML text order as reading order: select the first textual body and traverse nested sections in document order; do not narrate the notes body twice.
- Sending Latin text to Russian Silero: normalize known titles/names, URLs, symbols, and remaining Latin deterministically.
- Normalizing each tiny fragment independently: normalize at section assembly to avoid level pumping.
- Treating a chapter title like an ordinary paragraph: insert explicit silence before and after every spoken chapter title. Do not rely on the preceding paragraph pause or container chapter metadata to create audible separation.
- Trusting file existence: validate codec, channels, sample rate, duration, hashes, section order, chapter timing, and decodability.
- Calling a technical pass a listening pass: only the user can accept pronunciation, pacing, and naturalness.
- Expecting EQ or compression to create missing emotion: mastering can improve warmth, density, loudness, and comfort, but a flat performance requires different synthesis preparation, voice, or model.
- Treating marked stress from a demonstration as normal prose: most source texts contain no author-supplied stress marks; never add global guessed stress merely because a test example used them.


