# Optional mastering

Read this reference only when the user requests post-processing or accepts a mastered comparison sample. Mastering polishes an assembled performance; it does not supply missing emotion or repair unnatural prosody.

## Preserve the synthesis master

- Keep the unmastered assembled WAV and record its SHA-256.
- Process complete short samples or assembled section masters, never individual synthesis units.
- Write a temporary sibling, validate it, then rename it to the final path.
- Do not alter playback speed, pitch, or pauses in this profile.

## Proven warm-dense profile

This optional profile was selected over an unprocessed sample and a lighter audiobook master. Treat it as a tested starting point, not a universal default.

| Stage | Setting |
|---|---|
| High-pass | 60 Hz |
| Warmth | bass +1.5 dB around 120 Hz; +1 dB around 180 Hz |
| Treble | -0.8 dB around 5 kHz |
| Compression | threshold 0.1, ratio 2.2:1, attack 25 ms, release 250 ms, makeup 1.35 |
| Loudness | target -16 LUFS, LRA 9, true peak -1.5 dBTP |
| Output | PCM-16 WAV, 48 kHz, mono for sample/master comparison |

Example filter chain:

```powershell
ffmpeg -v error -i input.wav `
  -af "highpass=f=60,bass=g=1.5:f=120:w=0.6,treble=g=-0.8:f=5000:w=0.5,equalizer=f=180:t=q:w=1:g=1,acompressor=threshold=0.1:ratio=2.2:attack=25:release=250:makeup=1.35,loudnorm=I=-16:LRA=9:TP=-1.5" `
  -c:a pcm_s16le -ar 48000 -ac 1 output.tmp.wav
```

For an audiobook, apply the same tonal and compression profile at section-master assembly, then encode the validated deliverable format. Avoid normalizing short cached fragments independently.

## Efficient codec-aware finalization

For long books, decide the final codec path before starting the production encode.

- Measure the complete ordered mastered input once with loudnorm pass 1 and save `input_i`, `input_tp`, `input_lra`, `input_thresh`, and `target_offset` in the build logs.
- Run pass 2 with those measured values and a conservative pre-codec true-peak ceiling selected for the final encoder. Validate the decoded AAC output, because MP3/AAC intersample overshoot cannot be accepted from configured filter values alone.
- Preserve the pass-1 log and exact pass-2 filter in the verification report.
- Use short representative samples to choose tone and compression. Do not use repeated full-book encodes as a parameter search loop.
- A failed final measurement permits another full encode only after the failure has a specific technical cause and the correction is deterministic.
## Acceptance checks

Require fresh evidence for both the unmastered and mastered files:

- successful full-file decode and positive duration;
- expected codec, 48 kHz sample rate, and one channel;
- duration unchanged within container rounding tolerance;
- integrated loudness near -16 LUFS and true peak no higher than -1.5 dBTP;
- SHA-256 and byte size recorded;
- no clipping, pumping, harsh sibilance, excessive bass, or audible boundary changes in the listening comparison.

Report measured values rather than only the configured targets. Let the user choose between unmastered, lighter, and warm-dense samples when no mastering profile has already been accepted.
