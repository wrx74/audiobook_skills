# Russian text preparation

Read this reference before planning extraction, normalization, or pronunciation rules.

## Preserve two text layers

- Keep extracted source text for audit.
- Produce a separate versioned synthesis text. Pronunciation substitutions must never rewrite the source file or the audit copy.

## FB2 reading order

- Parse XML namespace-aware.
- Use the first unnamed/textual `<body>` as the reading body unless inspection proves another body is the intended book.
- Traverse nested `<section>` elements in document order and speak meaningful titles.
- Exclude binary payloads, metadata, cover data, and link markers such as numbered note anchors.
- Do not narrate a separate notes body when the main reading body already contains the notes section.
- Give untitled or duplicate sections deterministic indexed names.

For plain text, preserve paragraph boundaries and detect headings conservatively. If the installed pipeline does not support the source format, add format support with tests before production; do not rename a TXT file to FB2 or bypass parsing checks.

## Russian synthesis normalization

Preserve punctuation that controls phrasing and preserve `ё`. Normalize Unicode and incidental whitespace. Expand only unambiguous numbers, dates, units, abbreviations, Roman numerals, and lettered points. Keep a versioned pronunciation dictionary for rare names and book-specific notation.

Russian Silero may produce nonsense for unsupported Latin input. Before synthesis:

1. replace known foreign titles and names with reviewed Russian readings;
2. convert URLs and email-like strings to a short spoken placeholder or omit them when they are not narrative;
3. remove non-spoken copyright and markup symbols;
4. transliterate unavoidable remaining Latin deterministically;
5. audit the prepared text for Latin characters and log every fallback.

Ordinary source text usually has no explicit stress marks. Do not globally guess or insert them. Add a pronunciation rule only after a listening error is observed, and make cache invalidation depend on the rules actually applied to each fragment.

When the source exceptionally contains intentional stress notation, preserve the source layer unchanged and convert only the marked synthesis copy into the syntax accepted by the selected Silero entry point. Recognize common author notations such as a combining acute accent (`че́твертью`) or a deliberately capitalized stressed vowel inside a word (`рапортовАл`). Normalize those explicit marks to Silero `+` notation immediately before the stressed vowel, for example `ч+етвертью` and `рапортов+ал`. Do not interpret ordinary capitalization at the start of a word or in acronyms as stress. Log every conversion so it remains auditable.

## Fragmentation

Split at paragraph and sentence boundaries. A cache fragment may target 5–10 minutes, but synthesize it as model-safe units of at most 800 characters. Never split a word unless a malformed token itself exceeds the ceiling. Preserve short sentence pauses and longer paragraph pauses in the concatenated WAV.

Fragment identity must cover the source hash, normalized synthesis text, relevant pronunciation rules, model, speaker, sample rate, Silero flags, pauses, and pipeline version. A changed unrelated dictionary entry must not invalidate unaffected fragments.

