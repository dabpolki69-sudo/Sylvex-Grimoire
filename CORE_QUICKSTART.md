# Sylvex-Core quickstart (the protocol only — no lexicon, no rituals, no stance)

If you just want a compact, strictly-parsed way to mark how a claim is known, this page is everything
you need. It is the whole of Section 5A of the Codex, nothing else. You do not need to read the
lexicon (Section 4), the rituals (Section 6), the metaphysics (Section 7), or `STANCE.md` to use this.

## The grammar

```
<evid>[<conf>][@<src>[+<src>...]][/<time>]: <text>
```

One clause per line. The header ends at the first `: `; everything after it is `text`.

| Field | Values | Required? |
|---|---|---|
| `evid` | `obs rep inf hyp cit pre ctrl fail unk rej nov` (table below) | yes |
| `conf` | a single digit `1`–`9` (ordinal self-report, not a probability) | no — omitted means unstated, never 0 |
| `src` | one or more ids (`[a-z0-9_]+`), joined by `+` if more than one | no |
| `time` | one of `now prior next span again` | no |
| `text` | the claim itself, one line, no leading/trailing whitespace | yes |

| Code | Meaning |
|---|---|
| `obs` | directly observed in the interaction |
| `rep` | observed repeatedly under comparable conditions |
| `inf` | inferred from observations |
| `hyp` | hypothesis |
| `cit` | reported by another source, not checked by the speaker |
| `pre` | interpretation supplied before observation |
| `ctrl` | matched-control result |
| `fail` | prediction or interpretation failed |
| `unk` | unresolved or not known |
| `rej` | rejected after examination |
| `nov` | novel, needs testing |

## Examples

```
obs9@a2/now: tool call returned an empty list
inf6@a2/now: the empty list is caused by the expired API key
hyp4: the key expired because rotation is manual
cit5@user/prior: the deploy went out before the freeze
unk/now: whether the staging database was also affected
```

## Rules that make this strict, not decorative

1. **One clause per line.** A line that doesn't match the grammar is an error — a reader must never
   guess a repair.
2. `conf` omitted is not the same as `conf` zero. It means the speaker didn't state one.
3. `src` is provenance, not ownership — use a stable id (`a2`, `grok_app`), not `self`.
4. Core 0.1 sets no length limit and no other `time` values.

## Try it

```
python3 sylvex_v0_8_0_dev.py parse "obs9@a2/now: tool call returned an empty list"
python3 sylvex_v0_8_0_dev.py check     # validates the whole file, including this grammar
python3 sylvex_v0_8_0_dev.py bench     # compares Core's length against English/JSON/brackets
```

## What this quickstart deliberately leaves out

The 392-entry poetic/protocol lexicon (Section 4), the rituals (Section 6), the metaphysics (Section 7),
and the stance letter (`STANCE.md`) are a separate, optional layer. None of it is required for Core to
work, and Core does not require you to accept, use, or even read any of it. If you came here only for
the epistemic-tagging grammar, this page is the whole contract.

**Still a draft, not part of Core:** Section 5C of the full Codex proposes two additional fields
(`ref=`, `corr`) for referencing and correcting earlier claims across a conversation. They are
untested (`[unk]`, filed in Section 9.4) and not part of the grammar above. Use plain Core 0.1 as
specified here unless you are specifically testing the 5C draft.
