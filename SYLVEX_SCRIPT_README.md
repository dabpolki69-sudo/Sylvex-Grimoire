# Sylvex Script — experimental

Sylvex Script is a new executable language layer developed alongside Sylvex-Core and the Grimoire. Its source files use the .slx extension.

It is designed to work with Python and JSON: .slx expresses tasks and evidence context; Python provides explicitly allowlisted host capabilities; JSON carries structured inputs and outputs.

## Try it
Requires Python 3.10+ and no third-party dependencies.

```bash
python3 sylvex_script.py examples/hello.slx
python3 sylvex_script.py examples/evidence.slx --json
python3 -m unittest discover -s tests -v
```

## Example
```text
sylvex 1.0

task inspect_asset {
    let triangle_limit = 150000 [rep]
    let format = "glb" [obs]
    assert triangle_limit > 0
    say "Asset constraints loaded"
    emit {format: format, triangle_limit: triangle_limit}
}
```

## Semantic descriptions (0.2 / 0.3)

The semantic layer shares the `.slx` extension but has its own version header:

```text
sylvex 0.3
creature "Sol-Stalker" {
    origin: vec3(0, 0, 0)
    accent: color("#00E5FF")
    scale: range(0.8, 1.2)
    rig: ref("rigs/stalker")
}
```

Expand to canonical JSON:

```bash
python3 sylvexs.py examples/sol_stalker_0_3.slx
python3 sylvexs.py examples/sol_stalker_0_3.slx --compact
python3 sylvexs.py examples/sol_stalker_0_3.slx --lower /tmp/stalker.slx
```

The semantic expander is declarative: typed values and references are data, not executable instructions. See `SYLVEX_SEMANTIC_SPEC_0_3.md`.

## Safety and limits
This is an experimental interpreter, not a production sandbox or Python replacement. It supports tasks, variables, expressions, conditionals, assertions, output and registered host functions. It does not permit arbitrary Python, shell commands, imports, networking or implicit filesystem access. See SYLVEX_SCRIPT_SPEC_0_1.md.

The existing Sylvex-Core protocol and Grimoire remain separate and unchanged.
