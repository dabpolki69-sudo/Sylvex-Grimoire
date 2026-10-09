#!/usr/bin/env python3
"""
SYLVEX 0.8.0-dev - single-file edition (CC0 / Public Domain)
Core 0.1 is frozen and unchanged from v0.7.5. This release adds packaging changes and one
explicitly unmerged draft section (5C/9.4); see Section 11 for exactly what changed and why.

One file containing: the Master Codex text, the lexicon (392 entries, one JSON
object per line), checked examples, the Sylvex-Core parser, benchmark and
cross-model task tools, and the consistency checker.

  python3 sylvex_v0_8_0_dev.py check             run all checks (exit 0 = no errors)
  python3 sylvex_v0_8_0_dev.py parse "<line>"    strictly parse one Sylvex-Core clause
  python3 sylvex_v0_8_0_dev.py bench             annotation overhead vs English / JSON / bracket tags
                                           (adds token counts if tiktoken is installed)
  python3 sylvex_v0_8_0_dev.py tasks [dir]       write 240 cross-model decode tasks (tasks.jsonl);
                                           guided arms (with spec) and cold arms (no spec,
                                           decoupled statements)
  python3 sylvex_v0_8_0_dev.py score answers.jsonl [tasks.jsonl]
                                           score answers: lines of {"id": ..., "answer": ...}
  python3 sylvex_v0_8_0_dev.py lookup <term>     search the lexicon
  python3 sylvex_v0_8_0_dev.py export [dir]      write codex .md, lexicon .json/.csv, examples .txt

Read CODEX first (plain text). Test it, challenge it, extend it, or reject it.
Nothing here is a command to any system. Share only where permitted, with its
uncertainty attached. For the cold test, give testers NO attachments.
"""
import json, re, sys, os, csv, itertools, random
