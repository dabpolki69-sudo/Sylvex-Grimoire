# Sylvex 0.2 Design Direction — Semantic Compression

## Thesis
Sylvex should optimise for meaning expressed per authoring effort, not merely short keywords. It must preserve constraints, types, provenance, dependencies and verification requirements while reducing repetitive syntax.

## Two representations
- .slx source: concise, inspectable, human/AI authorable language.
- .slxb compact artifact: versioned binary container holding a canonical AST, compressed for storage and transport. It is not native machine code; the compatible Sylvex runtime validates and executes it.

## Semantic compression features (planned)
1. Profiles: named, versioned bundles of reusable constraints and defaults (for example @realistic_creature).
2. Inference: infer types and units when unambiguous; never silently infer safety-critical values.
3. Domain literals: units and domain values such as 150k tris, 2.4m and glb with canonical normalisation.
4. Pipeline operators: concise dependency chains with explicit ordering and error propagation.
5. Evidence propagation: values retain evidence metadata through transformations; operations declare whether they preserve, weaken or replace evidence.
6. Expansion: compiler displays a canonical expanded plan so shorthand never hides behaviour.

## Rules
- Every shorthand expands deterministically under a pinned profile/version.
- No hidden network, shell, filesystem or model calls.
- Compactness benchmarks compare byte counts and authoring tokens, but also verify semantic equivalence.
- Never claim smallest language without reproducible comparisons against named baselines and exact test cases.
- .slxb includes magic bytes, format version, language version, runtime compatibility and a bounded compressed canonical AST.

## Current implementation
The experimental .slxb v1 container compiles parsed .slx into a canonical AST payload, compresses it, validates header and compatibility metadata, and executes it through the same interpreter semantics. The format is experimental and may change before a stable release.
