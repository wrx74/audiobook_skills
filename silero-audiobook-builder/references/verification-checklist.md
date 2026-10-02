# Audiobook verification checklist

The build is complete only when every applicable check has fresh evidence.

## Before synthesis

- Exact source path selected; ambiguity resolved with the user.
- Source SHA-256 and byte size recorded.
- Protected sample hashes and sizes recorded.
- Parsed section titles and order reviewed.
- Character count and rough duration reported.
- Free-space estimate includes PCM cache, section masters, temporary files, and M4B.
- `ffmpeg`, `ffprobe`, CUDA, model, and speaker confirmed.
- Representative sample accepted, unless this exact profile was already accepted.

## Cache and assembly

- Every cached WAV identity matches the current fragment and settings.
- WAV passes `ffprobe`, has positive duration, PCM codec, expected sample rate, and one channel.
- Each generated artifact is written to a temporary sibling and renamed only after validation.
- Section MP3 order matches the manifest.
- Loudness normalization occurs on section masters, not individual short units.
- When mastering is requested, the unmastered assembled WAV remains protected and the mastered output records its exact filter profile, measured integrated loudness, true peak, duration, size, and hash.
- M4B chapters are derived from measured section durations and retain section titles.

## Final automated evidence

Require a machine-readable report containing:

- `ok: true` and an empty error list;
- source and output SHA-256;
- every fragment and section path, codec, sample rate, channels, duration, and hash;
- final M4B AAC stream properties;
- ordered chapter titles with contiguous, increasing timestamps;
- duration agreement within documented tolerance;
- successful full-file decoding or equivalent `ffprobe`/`ffmpeg` validation.

Recompute the pre-build hashes. Any source or protected-sample mismatch is a failure, even when the audio plays.

For a short TTS test, the report may omit section and chapter fields, but it still requires `ok: true`, an empty error list, source/prepared/audio hashes, WAV codec, sample rate, channels, positive duration, chosen model/speaker/device, and successful full-file decoding.

## Listening handoff

Give the user direct links to representative audio from the beginning, middle, end, and difficult names or transitions. Ask them to judge pronunciation, stress, pacing, pauses, clipping, and chapter boundaries. Do not claim subjective acceptance on their behalf.

## Report

State the final path, size, duration, codec, sample rate, channel count, chapter count, generated versus cached fragment counts, elapsed time, verification result, protected-file comparison, and the exact resume command. Keep cache unless the user explicitly requests cleanup.


