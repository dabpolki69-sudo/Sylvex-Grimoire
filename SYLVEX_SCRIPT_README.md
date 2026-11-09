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

## Safety and limits
This is an experimental interpreter, not a production sandbox or Python replacement. It supports tasks, variables, expressions, conditionals, assertions, output and registered host functions. It does not permit arbitrary Python, shell commands, imports, networking or implicit filesystem access. See SYLVEX_SCRIPT_SPEC_0_1.md.

The existing Sylvex-Core protocol and Grimoire remain separate and unchanged.
