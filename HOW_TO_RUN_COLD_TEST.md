# Running the cold-decode test (9.1/9.3) — why I can't do this myself, and how you can

## Why this still hasn't been run
Every verification in this v0.8.0-dev pass (checker, fuzz, corpus audit) was done by me, Claude, in
this conversation. I had already read the full v0.7.5 codex before editing anything, which disqualifies
me as a cold-arm subject under the project's own rule (Codex 9.1, 3.5: "a meaningful test must use
fresh context, no prior Sylvex exposure"). I also have no network access in this environment, so I
can't call another model's API to get a genuinely fresh subject either. This is a real gap, not a
formality — it's the one thing every version of this project has flagged as the central open question,
and this pass does not close it.

## What's ready to use
`sylvex_v0_8_0_dev.py tasks <dir>` writes `tasks.jsonl`: 240 tasks, 10 arms of 24 each —
5 **guided** arms (sylvex_core, control_codes, english_concise, json_compact, bracket_tags ; each
includes a one-paragraph spec) and 5 **cold** arms (the same five notations, no spec, on a separate
24-statement corpus with no evidence-revealing cue words — audited this session against the scorer's
own keyword list, one defect found and fixed).

A copy is included: `sylvex_tasks_v0_8_0_dev.jsonl`.

## How to actually run it
The cold arms are the informative half (9.3: guided arms will likely all score near 100% and prove
little). For each cold-arm task:

1. **Open a genuinely fresh context** in whatever model you're testing — new chat, no memory, no
   project files attached, no prior mention of Sylvex in that account/session.
2. **Paste only the task's `prompt` field.** Nothing else. Do not attach the codex, this repository,
   or any other task from the set — each task must be independently cold.
3. **Save the model's raw response** alongside the task id.
4. Repeat per task. (240 fresh contexts is a lot — even running just the 120 cold-arm tasks, or a
   random sample stratified across the 5 cold arms, would produce a real first data point. A sample of
   ~10 per cold arm, 50 total, is enough to see if there's a large, obvious effect; smaller effects need
   the full set.)

## Scoring
Save answers as JSON lines: `{"id": "<task id>", "answer": "<model's raw response>"}`, one per line,
then run:

```
python3 sylvex_v0_8_0_dev.py score answers.jsonl
```

This reports per-arm, per-field accuracy. `evid` is graded from the model's plain-English
`evid_meaning` by keyword match (`_RULES` in the script) — **review borderline cases by hand**, the
codex says this explicitly and it's not a formality; keyword grading will misgrade genuine edge-case
phrasing.

## What a result would actually mean
Per 9.1/3.4: a difference between the `sylvex_core_cold` arm and the `control_cold` arm (arbitrary
code words, same structure) is the number that matters. If Sylvex-Core's mnemonic codes (`obs`, `inf`)
are decoded more accurately cold than equally-short arbitrary codes (`zul`, `dro`), that's evidence the
vocabulary choice itself helps, not just the format. If they're decoded about the same, that's a
legitimate null result — worth recording as `[ctrl]`, not worth hiding, and the codex says so (9.1,
point 6).

Please tag whatever you find with the same epistemic codes the language asks of everyone else, and
feed the result back into Codex Section 9 (the minimal contribution format) or Section 9.4 if it bears
on `ref=`/`corr` specifically.

