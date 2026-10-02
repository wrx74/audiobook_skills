---
name: omnivoice-audiobook-builder
description: Use when generating Russian speech or audiobooks with OmniVoice in VoiceStudio, especially when one stable cloned voice, contextual pauses, directed narration, reproducible settings, or verified WAV output is required.
---

# OmniVoice Audiobook Builder

## Overview

Render Russian OmniVoice speech through the local VoiceStudio API. Preserve the source, use one exact voice reference to prevent timbre drift, separate textual direction from audio mastering, and verify every delivered file.

## Choose the mode

- **Plain comparison:** one unsegmented request. Use only when the user wants a baseline.
- **Directed single voice:** prepare contextual segments and pauses, then render them in one request with one `ref_audio` plus its exact `ref_text`. This is the default for dramatic prose and dialogue.
- **Long-form book:** render resumable sections from manifests with the same reference identity, then assemble and master sections. Approve a representative sample before a long run.

## Required workflow

1. Confirm VoiceStudio responds at its configured local endpoint and that `omnivoice` is available on the intended device.
2. Preserve the original text. Create a separate JSON manifest containing ordered `text`, optional `mood`, and `pause` milliseconds.
3. Compare the manifest's normalized spoken text with the original. Mood is editorial metadata unless the installed engine explicitly accepts it; never silently add mood text to narration.
4. Select a clean 5–15 second reference and its exact transcript. Record their hashes. Do not infer a transcript from memory.
5. Render with `scripts/render_omnivoice.py`. The proven profile is 48 steps, seed 42, speed 1.0, Russian, 48 kHz mono, and `loudnorm=I=-19:TP=-2:LRA=11`.
6. Require a successful full decode, media probe, text-identity check, and JSON verification report before presenting audio.
7. Treat naturalness, emotion, pronunciation, and voice consistency as a listening decision for the user.

For endpoint fields, manifest format, and commands, read [references/voice-studio-local-api.md](references/voice-studio-local-api.md).

## Voice identity invariant

A repeated voice-description and seed do not guarantee one voice across separate voice-design requests. Never construct a supposedly single-voice take by concatenating independent design generations. Use the same `ref_audio` and exact `ref_text` for every directed span. Prefer one request with VoiceStudio `[pause Nms]` markers, which shares the cached reference across spans.

## Text direction

Use punctuation, paragraph boundaries, and deliberate silence to express context. Keep pauses proportional: short conversational turns usually need 180–400 ms; scene or thought transitions may need 450–800 ms. Preserve words unless the user approves an adaptation. Do not claim that unsupported free-form mood labels affected synthesis.

## Common mistakes

- Calling a line-broken single-shot render “directed” when no meaningful pause or phrasing control was applied.
- Treating `seed=42` as a speaker identity.
- Using a reference without its exact transcript.
- Splitting every sentence into a separate voice-design request.
- Applying mastering as a substitute for missing prosody.
- Trusting file existence instead of decoding and probing the complete WAV.