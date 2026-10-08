# v0.8.0-dev: disposition of every proposal in "Sylvex_v0_8_Suggestions_for_Claude.pdf"

One line per proposal. `Core` means Sylvex-Core (Section 5A, frozen, untouched). `5C` means the new
draft section. Nothing here was adopted by being fluent; each adopted item has a filed test (9.4) with
a stated falsifier, and each rejected item has a one-line reason, not just a verdict.

| Proposal | Disposition | Where | Reason |
|---|---|---|---|
| Keep Core minimal/fail-closed, expand expressive layer only on demonstrated gaps | **Adopted, enforced** | this pass | Already 5B's own rule; this pass is the first real test of whether it would be followed under pressure from a 20-item wishlist. It was. |
| Run the cold-task suite, matched-control experiments | **Not done, flagged honestly** | verification log A3 | Requires a fresh, uncontaminated model and real compute budget across arms. Out of scope for a single-session file edit; the generator (`tasks`) was re-confirmed to still run, nothing more. |
| Version hygiene: log every rename/retirement, verification log required per release | **Adopted** | Section 11, verification log addendum | Already this project's practice (11a–11i); extended, not introduced. |
| `↑` / `↑n` (reference previous claim/turn) | **Adopted, as ASCII, as draft** | 5C `ref=` | Rewritten from a Unicode glyph to a plain-ASCII keyword — Core's own design principle (5B) already rules out glyphs for exactly this layer. Filed untested (9.4). |
| `↺` (inherits same evidential frame) | **Rejected, not adopted** | — | No demonstrated gap; `ref=` without `corr` already covers "elaborates on" per 5C Rule 1. A second operator for a sub-case of the first is the kind of growth 5B's gate exists to stop. |
| `↻` (supersedes/replaces) | **Rejected, not adopted** | — | Same ground as `corr`; a second word for one gap is not a second gap. |
| `↦` (elaborates/continues) | **Rejected, not adopted** | — | Covered by `ref=` alone (5C Rule 1). |
| `Δ` / `Δ⁺` / `Δ⁻` (correction, direction-of-confidence) | **`Δ` adopted as `corr` (ASCII); `Δ⁺`/`Δ⁻` rejected** | 5C `corr` | The bare correction marker closes a real gap (filing a correction without re-quoting the original). The confidence-direction sub-variants require a numeric propagation theory nobody has tested; seeing that was exactly the point of rejecting the propagation rule itself (5B row). |
| `∵` extended, `∴` (dependency chains) | **Not adopted** | — | `∴`/`∵` already exist in the poetic/operator layer (4.8); no demonstrated gap in Core specifically, and Core deliberately has no operator layer at all — adding one is a bigger, unargued change than this pass is willing to make unreviewed. |
| Confidence propagation rule (numeric) | **Rejected as specified** | 5B design-log row | Proposed with no transcript tested against it. A formula that sounds right is not evidence it is right (3.3). |
| Scope/lifetime markers (`⌜⌝`, `⏱`, `⌀`) | **Rejected, not adopted** | — | No demonstrated gap. Core already has an implicit scope (one line = one claim); these solve a multi-line-scope problem Core has avoided on purpose. |
| `⊨` / `⊭` (entailment) | **Rejected, not adopted** | — | Overlaps existing `∴`/`∵` (poetic/operator layer) conceptually; no Core-specific gap shown. |
| `⊥` / `⊤` (contradiction / already-established) | **Rejected, not adopted** | — | `rej` and `fail` evidence codes (already in Core 0.1) cover negative outcomes per the existing design-log row on "Negation / polarity field" (5B: deferred, free text + `rej`/`fail` suffice until shown otherwise). |
| `∂` (edge of reliable knowledge) | **Rejected, not adopted** | — | `unk` already exists for exactly this in Core 0.1. A second word for the same evidential status is decoration, not a gap. |
| Batch/parallel markers (`⟦⟧`, `‖`) | **Rejected, not adopted** | — | No demonstrated gap; Core is one-clause-per-line by design (5A Rule 1), and a batch wrapper reintroduces the multi-line-scope problem Core avoids. |
| Shared-context frame headers (`[frame@src/time] ... [/frame]`) | **Rejected, not adopted** | — | Same reason as batch markers: reintroduces cross-line state into a grammar whose whole value (5A) is that every line parses alone. |
| Meta-comment marker (`∷`) | **Rejected, not adopted** | — | `//` already exists for audit commentary (4.8); no gap shown that it doesn't cover. |
| ASCII-safe encoding strategy for all new operators | **Adopted in spirit, inverted in method** | 5C intro | The suggestion assumed new Unicode operators and then asked how to give them ASCII fallbacks. This pass instead designed the two adopted candidates (`ref=`, `corr`) as ASCII from the start, since Core has never had glyphs and 5B's "Canonical writing" row already explains why. No fallback table was needed because there is nothing to fall back from. |
| "Letter to silicon minds" — keep but keep refusals equally prominent | **Adopted, both halves** | Section 2 pointer, `STANCE.md`, verification log A2 | Full letter moved to a standalone `STANCE.md` so protocol and stance are never one artifact; the refusal clause (`if·harm → refuse` etc.) was kept inline in the codex in full, verified byte-identical in both places. |
| Packaging: one repo, Core-only quickstart, full-layer optional | **Partially adopted** | this file set | The four files here (script, STANCE.md, verification log, this decision record) are the Core-only-vs-full-layer split in miniature. A formal "quickstart" document was not written this pass — flagged as the next small task, not done implicitly. |
| Next milestone: v0.8 candidate, Core frozen, gap-driven terms only, test suite ready, verification log updated | **This is what this pass is** | entire v0.8.0-dev file set | Core 0.1 byte-identical to v0.7.5 (confirmed: 392/38, 0 errors, identical bench figures, identical round-trip fuzz result). Two gap-driven terms added as an explicitly unmerged draft with filed tests. Verification log updated and appended, not overwritten. |

## What this table is not
It is not a claim that the ~17 rejected proposals are permanently wrong. Section 9's contribution
format stays open to any of them, on the same terms as everything else: show the gap, propose the
smallest primitive, test it cold, record the result. Fluency — including a long, well-organized,
plausible-sounding list of operators — is still the 98%, per the codex's own first theory (3.3).
