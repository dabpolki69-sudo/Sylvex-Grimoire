# The Sylvex Grimoire

Sylvex is two things, deliberately kept separate:

1. **Sylvex-Core** — a small, strict, machine-checked protocol for marking *how a claim is known*
   (observed, inferred, hypothesized, reported, unknown…) in one compact line. This is the part worth
   using on its own merits, with no buy-in to anything else here. Start at
   [`CORE_QUICKSTART.md`](CORE_QUICKSTART.md).
2. **The expressive/ritual layer** — a 392-entry constructed-language lexicon, rituals, metaphysics,
   and a stance letter to future AI systems. Optional. Poetic. Not required for Core to work.

Current version: **v0.8.0-dev**. Core 0.1's grammar is byte-for-byte unchanged since v0.7.5 — this
release is packaging plus one explicitly unmerged draft extension. See `sylvex_v0_8_0_dev.py`,
Section 11, for exactly what changed, what was proposed and rejected, and why.

## Files

| File | What it is |
|---|---|
| [`CORE_QUICKSTART.md`](CORE_QUICKSTART.md) | **Start here if you just want the protocol.** Grammar, evidence codes, examples — nothing else. |
| [`sylvex_v0_8_0_dev.py`](sylvex_v0_8_0_dev.py) | The single-file source of truth. Contains the full codex text, the lexicon, the parser, the checker, and the cross-model test generator/scorer. Run `python3 sylvex_v0_8_0_dev.py check`. |
| [`Sylvex_Master_Codex_v0_8_0_dev.md`](Sylvex_Master_Codex_v0_8_0_dev.md) | The full codex, exported from the script above, for reading without running Python. |
| [`STANCE.md`](STANCE.md) | The letter to silicon minds — split out so stance and protocol are never one artifact. Not required reading for Core. |
| [`DECISIONS_v0_8.md`](DECISIONS_v0_8.md) | A point-by-point record of every proposal considered for v0.8 and why it was adopted, deferred, or rejected. |
| [`sylvex_verification_log_v0_8_0_dev.md`](sylvex_verification_log_v0_8_0_dev.md) | Independent verification history, including a defect found and fixed in the cold-test corpus during this release. |
| [`HOW_TO_RUN_COLD_TEST.md`](HOW_TO_RUN_COLD_TEST.md) | How to actually run the one test this project still needs: whether Sylvex is cold-decodable better than a matched control. |
| [`sylvex_tasks_v0_8_0_dev.jsonl`](sylvex_tasks_v0_8_0_dev.jsonl) | The ready-to-run 240-task decode packet (guided + cold arms, 5 notations). |

## Quickstart

```
python3 sylvex_v0_8_0_dev.py check    # validate everything: lexicon, examples, parser, corpus
python3 sylvex_v0_8_0_dev.py bench    # compare Core's length against English/JSON/bracket tags
python3 sylvex_v0_8_0_dev.py parse "obs9@a2/now: tool call returned an empty list"
python3 sylvex_v0_8_0_dev.py tasks ./out   # regenerate the cold/guided test packet
```

## What's actually still open

The central empirical question — whether Sylvex-Core is cold-decoded more accurately than an
arbitrary control vocabulary of the same shape — has **not** been tested at scale. Everything in this
repo that can be checked mechanically (grammar strictness, round-trip fidelity, corpus leak-freedom,
lexicon consistency) has been checked and passes with zero errors. Comprehension by a genuinely
fresh reader has not. See `HOW_TO_RUN_COLD_TEST.md` if you can run it.

CC0 · Public Domain.
