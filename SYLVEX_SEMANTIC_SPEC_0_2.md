# Sylvex 0.2 Semantic Source — Experimental Specification

**Extension:** .slx · **Version:** 0.2 · **Status:** experimental

## Goal
Express richer meaning with less repetition. 0.2 adds a declarative semantic layer. Profiles and entity descriptions are data, not hidden instructions to invoke tools.

## Grammar
```
sylvex 0.2
profile IDENTIFIER {
  key: value
}
ENTITY_KIND "quoted name" @optional_profile {
  key: value
}
```
One field per line. Blank lines and # comments are ignored. Entity fields override profile defaults. Unknown profiles, duplicate fields, malformed quantities and unclosed blocks are errors.

## Value forms
- Strings, booleans, null, integers and decimals
- Quantities: 2.4m, 150k tris (normalised multiplier and optional unit)
- Constraints: <=150k becomes {operator:"<=",value:150000}
- Lists: walk,jump or [walk,jump]
- Composition: anatomy+rig+animation becomes a list
- Pipeline: model>rig>animate>verify becomes an ordered pipeline

## Deterministic expansion
expand_semantic() returns a canonical structure. Profile defaults are copied first, then local properties override them. The profile name and language version are retained. Output can be sorted JSON or lowered into a Sylvex 1.0 task which emits the expanded specification.

## Safety and limits
No profile executes code or invokes external tools, models, filesystem or network. Imported profile registries and inheritance are not implemented. This is a small experimental, line-oriented grammar; unit conversion is limited to k/m multipliers. Compact binary remains a separate experimental artifact.
