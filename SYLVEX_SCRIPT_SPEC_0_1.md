# Sylvex Script Language Specification — Draft 0.1

**Status:** experimental reference implementation · **Extension:** .slx · **License:** MIT

## Purpose
Sylvex Script is a small deterministic language for tasks, data, assertions and explicitly authorised operations. Its distinguishing feature is that values may carry evidence annotations describing how they are known. It complements Sylvex-Core; it does not replace it. Python supplies host capabilities and JSON carries structured data.

## Supported 0.1 features
- Header: sylvex 1.0; named task blocks.
- Scalar literals, lists, maps, variables and arithmetic/comparison/boolean expressions.
- let, set, say, emit, assert, if and else statements.
- Evidence annotations on variable assignments.
- Explicitly registered host functions and JSON-compatible results.
- Configurable statement execution-step limit.

## Grammar sketch
```ebnf
program   = "sylvex" "1.0", newline, { task } ;
task      = "task", identifier, block ;
block     = "{", { statement }, "}" ;
statement = let | set | say | emit | assert | call | if ;
let       = "let", identifier, "=", expression, [ evidence ] ;
set       = "set", identifier, "=", expression, [ evidence ] ;
evidence  = "[", evidence_code, "]" ;
call      = "call", identifier, "(", [ arguments ], ")" ;
if        = "if", expression, block, [ "else", block ] ;
```

Statements may be separated by newlines or unambiguous token boundaries. # begins a line comment. Evidence codes: obs, rep, inf, hyp, cit, pre, ctrl, fail, unk, rej, nov. An annotation is metadata, not a probability or proof of truth. The interpreter preserves it but does not validate the claim.

## Safety contract
The interpreter never uses eval/exec, imports from .slx, shell commands, implicit I/O or network access. Host functions are callable only when supplied by the embedding application in an explicit allowlist. Applications must expose narrow, validated capabilities and apply their own permissions and resource controls. The step limit is not a complete sandbox.

## Interoperability
Python embeds the interpreter with Interpreter(functions={...}).run(source). Registered functions receive plain Python values. Results contain task, output, emitted values, variables and step count. Evidence-bearing values serialize as {value: ..., evidence: ...}.

This is an experimental 0.1 implementation, not a frozen 1.0 language specification. Breaking grammar changes require an explicit language-version change.
