# Sylvex 0.3 Semantic Source — Experimental Specification

**Extension:** .slx · **Version:** 0.3 · **Status:** experimental

## Purpose
Sylvex 0.3 adds typed semantic values and explicit references while preserving deterministic expansion and 0.2 compatibility. The semantic layer describes data and relationships; it does not execute tools or resolve external assets.

## Source form
```
sylvex 0.3
profile realistic {
  material: pbr
  motion: natural
}
creature "Sol-Stalker" @realistic {
  origin: vec3(0, 0, 0)
  accent: color("#00E5FF")
  scale: range(0.8, 1.2)
  rig: ref("rigs/stalker")
}
```

## Typed constructors
- `vec3(x, y, z)`: exactly three numeric coordinates.
- `color("#RRGGBB")` or `color("#RRGGBBAA")`: validated hexadecimal color, normalised to uppercase.
- `range(min, max)`: two numeric bounds with min no greater than max.
- `ref("path-or-id")`: explicit symbolic reference. It is data only; it does not load or execute the target.

Invalid constructor names, argument counts and value types are errors. Nested constructors and lists are parsed deterministically.

## Relationships
References nested in entity properties form directed graph edges. `relationship_edges()` extracts edges with their originating property path. References may name assets, rigs, animations, materials or other entities; this stage does not require targets to exist, since resolution belongs to a later validation layer.

## Expansion and compatibility
The 0.3 header is retained in expanded output and profile version metadata. Existing 0.2 source remains valid. Profile defaults are copied first and entity-local values override them. Canonical JSON remains available, and lowering continues to emit native Sylvex 1.0 values.

## Safety and limits
No constructors execute code. No implicit filesystem, network, model or tool access exists. References are inert identifiers. Units are not yet dimensionally converted; `2.4m` preserves its numeric value and unit. This is an experimental line-oriented grammar, not yet a production sandbox or a claim of superior compactness.


## Validation CLI

Validation is local and deterministic. It does not open referenced resources.

```bash
# Check entity identifiers and document structure
python sylvexs.py examples/sol_stalker_0_3.slx --validate

# Require every ref() to appear in an explicit registry
python sylvexs.py examples/sol_stalker_0_3.slx --strict-refs \
  --known-ref rigs/sol_stalker \
  --known-ref animations/stalker_locomotion
```

Use `--known-ref` multiple times to build the exact registry for a project. Strict validation without a registry is an error; no paths are read or resolved automatically.
