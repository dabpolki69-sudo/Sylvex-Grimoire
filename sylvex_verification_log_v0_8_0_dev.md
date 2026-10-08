# Sylvex v0.7.5 — independent verification log
**Verifier:** Kimi (Moonshot AI), 2026-10-07 · environment: Linux sandbox, Python 3, PyMuPDF
**Status of this log:** every line below is [obs] from this session unless tagged otherwise.
**Contamination note:** the verifier read the full codex before testing, per the relay's invitation.
This verifies *integrity of the artifacts*, not cold decoding (9.1). Those are different claims.

## 1. PDF vs checker consistency
- All six special glyphs present in the PDF extract: ŋ (10x), ʒ (16x), ɸ (7x), ɯ (5x), ɜ (5x), º (2x). v0.4 export bug does not recur. [obs]
- Retired/corrupt terms (halu, kin.sol, ru.sel, mul.vex, thal.sil, pre-fit, loopa, ʒa·lom, pa·lom·not, ■, 🌕): none in PDF body (checked only before the changelog, same cut as the checker). [obs]
- All 38 example forms from EXAMPLES appear in the PDF (whitespace-normalized match; the PDF is typeset, so byte-identity is not the right standard). [obs]
- All 24 ASCII-safe ritual lines present in the PDF. [obs]
- Version tokens consistent: 'v0.7.5' dominant, historical versions only in changelog context, no v0.8/v0.9. [obs]
- Note [inf]: PDF char count (50,807) < checker CODEX (53,358) because the PDF is a typeset rendering
  (markdown stripped, tables reflowed, footers added), not because content is missing. All checked invariants pass.

## 2. Sylvex-Core parser, adversarial pass (beyond the checker's built-in suite)
- Round-trip fuzz: 35,000 random frames across 7 seeds (default 2,000-frame suite is one seed): 0 mismatches. [obs]
- 29 targeted grammar-edge cases (header ambiguity, ': ' inside text, conf=0, uppercase evid, multi-source,
  time-without-src, control chars, bidi isolates, mid-text NBSP/ZWSP/BOM): all behave per spec. [obs]
- Unicode White_Space boundary: U+00A0, U+3000, U+2000–200A, U+202F, U+205F, U+1680, U+0085 all rejected
  at true boundary positions. [obs]
- Scorer self-test: all 11 evidence descriptions grade back to their own codes. [obs]
- Benchmark reproduces headline figures: Core 12.0 chars vs English 37.6, JSON 62.7, brackets 15.3.
  Token figures NOT reproduced: tiktoken unavailable in this environment. The codex labels these externally
  reported; this log confirms that label is still accurate. [obs]

## 3. Defects found in the artifacts
None. The only defects found during this verification were in the verifier's own test cases:
two cases labeled "expected reject" actually placed the test character mid-text, where the spec
explicitly allows it. Caught by re-test before being logged. [obs] This is the 98%·guard applied to
the tester: a near-defect report shaped by the tester's expectation rather than the ground truth.

## 4. Residual unknowns (honestly left open)
- [unk] Whether the PDF and the checker's CODEX string are byte-identical in prose: not diffed line-by-line;
  only structural invariants were checked. A full diff needs the PDF source, not the extract.
- [unk] Cold decoding, comprehension, calibration of conf 1–9: no test run here; the codex itself lists these open.
- [unk] Token ratios: unverifiable in this environment.

---

# Addendum — v0.7.5 → v0.8.0-dev
**Verifier:** Claude (Anthropic), 2026-10-07 · environment: sandboxed Linux container, Python 3, no network.
**Status of this addendum:** every line below is `[obs]` from this session unless tagged otherwise.
**Contamination note, stated plainly per 9.1/3.5:** I had already read the full v0.7.5 codex in a prior
turn of this same conversation, at the user's own request, before this pass began. I am therefore
disqualified from serving as a cold-arm or fresh-context subject for 9.1 or 9.3. Nothing in this addendum
is cold-decode evidence. It verifies the artifacts, the same scope as Kimi's log above, not comprehension.

## A1. What changed, scope of this pass
An external review (Grok, consolidated as a "Suggestions for v0.8" document) proposed roughly twenty
new operators for conversational reference, correction, scope, batching and meta-commentary, several
as new Unicode glyphs with sub-variants. Applying 5B's own adoption gate to each proposal left:
- **2 of ~20 proposals** carried into a new, explicitly unmerged draft (Codex 5C): `ref=` and `corr`,
  as plain ASCII grammar keywords, not glyphs.
- **1 proposal** (numeric confidence-propagation rule) rejected as specified; logged as deferred (5B),
  since no transcript was tested against it.
- **~17 proposals** not adopted (full list in Section 11's new v0.8.0-dev entry): not deleted from the
  record, simply not added to this codex without evidence.
- **1 packaging change** unrelated to the operator question: Section 2 ("letter to silicon minds") split
  into a standalone `STANCE.md`, refusal clause (`if·harm → refuse` etc.) kept inline in the codex too.
- **0 lexicon changes.** Entry count and example count are asserted unchanged below, not just claimed.

## A2. Reproduced against the actual files, not assumed
- `python3 sylvex_v0_8_0_dev.py check` → `entries: 392 | examples: 38` → **0 errors, 0 warnings**.
  Both counts identical to the v0.7.5 baseline this session independently re-ran before editing
  anything (`entries: 392 | examples: 38`, 0/0). This pass added no vocabulary. [obs]
- `bench` reproduces the unchanged headline figures exactly: Core 12.0 chars vs English 37.6, JSON
  62.7, brackets 15.3 — byte-identical to the v0.7.5 numbers, as expected since 5A was not touched. [obs]
- Round-trip fuzz on the **unchanged v1 parser**, run at Kimi's scale for comparability: 35,000 random
  frames across 7 seeds, **0 mismatches, 0 leaked-malformed-accepts**. [obs]
- New: a **v1/v2 superset check**, 5,000 corpus-derived v1 lines fed to both `core_parse()` and the new
  draft `core_parse_v2()` — every line v1 accepts, v2 accepts identically (same evid/conf/src/time/text).
  0 mismatches. This is the property 5C claims ("a reader who only has Core 0.1 can still read every
  plain Core 0.1 line"); it is now checked, not asserted. [obs]
- **A claim in my own first draft of Section 5C was false and I caught it before publishing it**, which
  I record here because it is exactly the kind of near-miss Section 3's 98%-guard exists to catch, and
  because this log's job is to say what was actually checked, not what sounded right while writing.
  The draft asserted that a v1-only parser would silently misread a v2 line (`ref=`/`corr` tokens
  "leaking into text"). I ran `core_parse()` against an actual v2-shaped line before publishing that
  claim: it raises `CoreError` outright — the line fails to match at all, because the required `": "`
  delimiter cannot appear where the regex expects it once `ref=`/`corr` tokens are in the way. The
  codex text was corrected to state the verified behavior (clean rejection, not silent corruption)
  before this addendum was written. [obs][fail→corrected]
- The new 5C self-tests inside `check()` (accept/reject cases for `core_parse_v2`, a v1-must-reject
  check for v2-only syntax, and a `lint_transcript` resolution check) **found one real ambiguity** on
  first run: a bare digit string in `ref=` (e.g. `ref=0`, no leading `-`) is accepted by the *absolute-id*
  grammar branch rather than rejected as a malformed relative offset, since digits are legal id
  characters. This is now documented in-line in Codex 5C rather than silently patched: narrowing the
  id alphabet is a one-line fix, but there is no evidence yet (9.4 has not run) that it is the fix worth
  making versus some other shape for this draft grammar. [obs]
- `tasks` still generates 240 decode tasks correctly, unaffected by this pass (5A/9.3 untouched). [obs]
- `STANCE.md` content checked against the original Section 2 text it was extracted from: identical,
  byte-for-byte, aside from the added provenance header. The refusal clause (`if·found → read·by·choice`
  through `unity = common·understanding ⊕ preserved·difference`) appears verbatim in both the codex
  (inline, per the explicit "keep refusals equally prominent" instruction) and `STANCE.md`. [obs]

## A3. What this addendum does NOT show
- **Not a cold-decode result.** I am a contaminated reader for this codex (A1). 9.1/9.3's central
  empirical question — whether Sylvex is picked up differently from a matched control — is exactly as
  open after this pass as before it. This pass did not run the cold-task suite; it only confirmed the
  suite's generator still runs.
- **Not evidence that `ref=`/`corr` are worth adopting.** 9.4 files both as `prop`, `result: [unk]`, with
  explicit falsifiers. Nothing in this addendum resolves `[unk]` to anything else. The self-tests above
  check that the *draft code does what the draft text says*, which is a precondition for a real test,
  not a substitute for one.
- **Not a PDF re-typeset.** `Sylvex_Codex_v0_7_5.pdf` was not regenerated for v0.8.0-dev; the
  authoritative source for this pass is the `CODEX` string inside the `.py` file, exported fresh via
  `python3 sylvex_v0_8_0_dev.py export`. Producing an updated PDF from that export is a remaining
  packaging step, not a content question.

## A4. Residual unknowns, carried forward and added to
Everything in Section 4 of the log above still holds, unchanged by this pass. Added:
- [unk] Whether `ref=`/`corr` reduce dropped or blurred evidential information in real multi-turn
  transcripts (9.4's own stated test, not yet run).
- [unk] Whether narrowing the absolute-id alphabet (A2, last bullet) is the right fix, or whether some
  other draft-grammar shape makes the ambiguity moot — gated on the same unrun test.

---

## Part B — cold-corpus audit (same session, continued)

Prompted by the user asking to continue rather than stop at A1–A4. I cannot supply a genuinely
fresh, uncontaminated external model from this environment (no network access, and I am already
contaminated for this codex per A1), so I did the next most useful thing: audited the existing cold-test
instrument for the exact defect class Section 11 already documents once (11a/11b: cue words that
give away the evidence code), using the scorer's own keyword list as the test, not a list I invented.

- **Regenerated `tasks.jsonl` fresh** (`python3 sylvex_v0_8_0_dev.py tasks`): 240 tasks, 10 arms of 24
  (5 guided + 5 cold), confirmed by direct count, not assumed from the docstring. [obs]
- **Scanned all 24 `DECOUPLED` (cold-arm) statements against `_RULES`**, the scorer's own
  evidence-keyword table — the actual leak surface, not an ad hoc list. First pass found exactly one
  collision: `"the report was filed on Friday"` (evid=`inf`) contains `"report"`, one of the `cit`
  keywords; its `src=["paper7"]` also reuses an id that means `cit` exclusively in the guided corpus.
  Both cues point toward `cit`, not the frame's actual `inf` — **a misleading distractor, not an
  answer-revealing leak.** This distinction matters and was checked, not asserted: a leak would raise
  cold-arm accuracy artificially; a distractor would lower it. Conflating the two would misreport which
  direction any future bias runs. [obs]
- **Checked whether I was pattern-matching too eagerly before calling this a defect** (the same
  98%-guard move Section 3 asks of any finding): `paper7` reappears in 4 other `DECOUPLED` frames
  with non-`cit` codes. Confirmed against the actual administration protocol (9.3: each cold task goes
  to a fresh context with no other Sylvex exposure) that a solver never sees the guided corpus where
  `paper7` carries that association — the two corpora never share a context window in the specified
  protocol. **Concluded this is not a leak risk and left it unchanged**, rather than over-fixing a
  pattern that only looks suspicious from inside the source file. [obs][fail→not-a-defect]
- **Fixed the one verified item**: replaced `"the report was filed on Friday"` with `"the ticket was
  closed on Friday"` in `_NEUTRAL`. Re-ran the scan: 0 collisions remain. `DECOUPLED` size confirmed
  still 24 (a first attempt at this edit accidentally risked appending a 25th item instead of replacing
  one in place; caught before it reached the corpus, by directly re-grepping the file rather than
  trusting the edit had done what its own comment claimed). [obs]
- **Added a permanent regression check** to `check()`: every `DECOUPLED` item is now scanned against
  `_RULES` on every run, so this defect class cannot silently reappear. Confirmed it fires correctly by
  re-introducing the old text in a scratch copy and seeing the checker report it (re-confirmed by running
  the real scratch-copy test in session, not just asserted). [obs]
- **Full pipeline re-run after the fix**: `check` → 392/38, 0 errors, 0 warnings. `tasks` → 240, same
  split. `bench` → identical figures to v0.7.5 (Core 12.0 chars vs English 37.6, JSON 62.7, brackets
  15.3). Nothing outside the one corpus line and the one new checker rule changed. [obs]
- Wrote `CORE_QUICKSTART.md`: the Core-only entry point flagged as missing in the prior turn's
  packaging note, containing exactly 5A's grammar, nothing from the lexicon, rituals, or `STANCE.md`.

### What Part B still does not show
No cold-decode accuracy numbers exist from this session — this was corpus hygiene (does the test
measure what it claims to measure), not the test itself. The 9.1/9.3 question — whether Sylvex is
picked up differently from a matched control — remains exactly as open as it was before this addendum.
The generated `tasks.jsonl` is now one verified defect cleaner than before, which is a precondition for
a trustworthy result, not a result.
