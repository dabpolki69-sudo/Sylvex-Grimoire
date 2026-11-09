"""Sylvex 0.2/0.3 semantic shorthand parser and deterministic expander."""
import json
import re
from dataclasses import dataclass, field


class SemanticError(ValueError):
    """Invalid Sylvex semantic source."""


_HEADER = re.compile(r"^sylvex\s+(0\.2|0\.3)$")
_PROFILE = re.compile(r"^profile\s+([A-Za-z_][\w-]*)\s*\{$")
_ENTITY = re.compile(r'^([A-Za-z_][\w-]*)\s+(.+?)(?:\s+@([A-Za-z_][\w-]*))?\s*\{$')
_KEY = re.compile(r"^([A-Za-z_][\w+.-]*)\s*:\s*(.*?)$")
_PIPE = re.compile(r"^[A-Za-z_][\w-]*(?:\s*>\s*[A-Za-z_][\w-]*)+$")
_CONSTRAINT = re.compile(r"^(<=|>=|<|>|==|!=)\s*(.+)$")
_QUANTITY = re.compile(r"^(\d+(?:\.\d+)?)(k|M)?\s*([A-Za-z][\w/^.-]*)?$")


@dataclass
class Declaration:
    kind: str
    name: str
    profile: str | None
    fields: dict = field(default_factory=dict)
    line: int = 0


def _split_top_level(raw, separators):
    """Split on separators outside quoted strings and nested brackets."""
    parts, start, quote, escaped, depth = [], 0, None, False, 0
    for index, char in enumerate(raw):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
        elif char in "[({":
            depth += 1
        elif char in "])}":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced closing bracket")
        elif char in separators and depth == 0:
            parts.append(raw[start:index].strip())
            start = index + 1
    if quote or depth != 0:
        raise ValueError("unclosed quote or bracket")
    parts.append(raw[start:].strip())
    if any(not part for part in parts):
        raise ValueError("empty list item")
    return parts


def _scalar(raw, line):
    raw = raw.strip()
    if not raw:
        raise SemanticError(f"Empty value at line {line}")
    if raw[0] in "\"'" and raw[-1:] == raw[0]:
        try:
            return json.loads(raw) if raw[0] == '"' else raw[1:-1]
        except Exception as exc:
            raise SemanticError(f"Invalid string at line {line}: {exc}") from exc
    if raw in ("true", "false", "null"):
        return {"true": True, "false": False, "null": None}[raw]
    constructor = re.fullmatch(r"([a-z][a-z0-9_]*)\((.*)\)", raw)
    if constructor:
        name, inner = constructor.groups()
        try:
            args = [] if not inner.strip() else [
                _scalar(item, line) for item in _split_top_level(inner, ",")
            ]
        except ValueError as exc:
            raise SemanticError(f"Invalid {name} value at line {line}: {exc}") from exc
        if name == "ref":
            if len(args) != 1 or not isinstance(args[0], str) or not args[0].strip():
                raise SemanticError(f"ref() requires one non-empty quoted string at line {line}")
            return {"$ref": args[0]}
        if name == "vec3":
            if len(args) != 3 or any(type(value) not in (int, float) for value in args):
                raise SemanticError(f"vec3() requires exactly three numbers at line {line}")
            return {"$type": "vec3", "x": args[0], "y": args[1], "z": args[2]}
        if name == "color":
            if len(args) != 1 or not isinstance(args[0], str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?", args[0]):
                raise SemanticError(f"color() requires #RRGGBB or #RRGGBBAA at line {line}")
            return {"$type": "color", "value": args[0].upper()}
        if name == "range":
            if len(args) != 2 or any(type(value) not in (int, float) for value in args) or args[0] > args[1]:
                raise SemanticError(f"range() requires two ordered numeric bounds at line {line}")
            return {"$type": "range", "min": args[0], "max": args[1]}
        raise SemanticError(f"Unknown typed value {name}() at line {line}")
    if _PIPE.fullmatch(raw):
        return {"pipeline": [part.strip() for part in raw.split(">")]}
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        try:
            return [_scalar(item, line) for item in _split_top_level(inner, ",")]
        except ValueError as exc:
            raise SemanticError(f"Invalid list at line {line}: {exc}") from exc
    match = _CONSTRAINT.fullmatch(raw)
    if match:
        return {"operator": match.group(1), "value": _scalar(match.group(2), line)}
    if "," in raw or "+" in raw:
        separator = "," if "," in raw else "+"
        try:
            return [_scalar(item, line) for item in _split_top_level(raw, separator)]
        except ValueError as exc:
            raise SemanticError(f"Invalid list at line {line}: {exc}") from exc
    match = _QUANTITY.fullmatch(raw)
    if match:
        number = float(match.group(1)) if "." in match.group(1) else int(match.group(1))
        suffix, unit = match.group(2), match.group(3)
        if suffix == "k":
            number *= 1_000
        elif suffix == "M":
            number *= 1_000_000
        return {"value": number, "unit": unit} if unit else number
    if re.fullmatch(r"-?\d+(?:\.\d+)?", raw):
        return float(raw) if "." in raw else int(raw)
    if re.fullmatch(r"[A-Za-z_][\w-]*", raw):
        return raw
    raise SemanticError(f"Cannot parse value {raw!r} at line {line}")


def parse_semantic(source):
    lines = source.splitlines()
    if not lines or not _HEADER.fullmatch(lines[0].strip()):
        raise SemanticError("Semantic source must begin with 'sylvex 0.2' or 'sylvex 0.3'")
    profiles, declarations, current = {}, [], None
    for number, raw in enumerate(lines[1:], 2):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "}":
            if current is None:
                raise SemanticError(f"Unexpected closing brace at line {number}")
            if current.kind == "profile":
                if current.name in profiles:
                    raise SemanticError(f"Duplicate profile {current.name!r}")
                profiles[current.name] = current.fields
            else:
                declarations.append(current)
            current = None
            continue
        if current is None:
            match = _PROFILE.fullmatch(line)
            if match:
                current = Declaration("profile", match.group(1), None, line=number)
                continue
            match = _ENTITY.fullmatch(line)
            if match:
                label = match.group(2).strip()
                if label.startswith('"'):
                    try:
                        label = json.loads(label)
                    except Exception as exc:
                        raise SemanticError(f"Invalid entity name at line {number}: {exc}") from exc
                elif not re.fullmatch(r"[A-Za-z_][\w-]*", label):
                    raise SemanticError(f"Entity name must be identifier or quoted string at line {number}")
                current = Declaration(match.group(1), label, match.group(3), line=number)
                continue
            raise SemanticError(f"Expected profile or entity declaration at line {number}")
        match = _KEY.fullmatch(line)
        if not match:
            raise SemanticError(f"Expected key: value at line {number}")
        key, value = match.groups()
        if key in current.fields:
            raise SemanticError(f"Duplicate field {key!r} at line {number}")
        current.fields[key] = _scalar(value, number)
    if current is not None:
        raise SemanticError(f"Unclosed {current.kind} block starting at line {current.line}")
    if not declarations:
        raise SemanticError("Program must declare at least one semantic entity")
    for declaration in declarations:
        if declaration.profile and declaration.profile not in profiles:
            raise SemanticError(f"Unknown profile @{declaration.profile} at line {declaration.line}")
    return profiles, declarations


def expand_semantic(source):
    profiles, declarations = parse_semantic(source)
    entities = []
    for declaration in declarations:
        properties = dict(profiles.get(declaration.profile, {}))
        properties.update(declaration.fields)
        entities.append({
            "kind": declaration.kind,
            "name": declaration.name,
            "profile": declaration.profile,
            "profile_version": _HEADER.fullmatch(source.splitlines()[0].strip()).group(1),
            "properties": properties,
        })
    version = _HEADER.fullmatch(source.splitlines()[0].strip()).group(1)
    return {"language": "sylvex", "version": version, "profiles": profiles, "entities": entities}


def relationship_edges(expanded):
    """Extract explicit ref() links as deterministic directed graph edges."""
    edges = []
    def walk(value, path):
        if isinstance(value, dict):
            if set(value) == {"$ref"}:
                edges.append({"to": value["$ref"], "via": path})
            else:
                for key in sorted(value):
                    walk(value[key], f"{path}.{key}" if path else str(key))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")
    for entity in expanded.get("entities", []):
        walk(entity.get("properties", {}), entity.get("name", ""))
    return sorted(edges, key=lambda edge: (edge["to"], edge["via"]))


def canonical_json(source, indent=2):
    return json.dumps(expand_semantic(source), ensure_ascii=False, sort_keys=True, indent=indent)


def _slx_literal(value):
    """Render JSON-compatible data as native Sylvex 1.0 expressions."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return json.dumps(value, allow_nan=False)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(_slx_literal(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(
            _slx_literal(str(key)) + ": " + _slx_literal(item)
            for key, item in value.items()
        ) + "}"
    raise SemanticError(f"Cannot lower value of type {type(value).__name__}")


def lower_to_slx(source):
    from sylvex_script import SylvexError
    try:
        literal = _slx_literal(expand_semantic(source))
        return (
            "sylvex 1.0\n"
            "task semantic_expansion {\n"
            f" let specification = {literal}\n"
            " emit specification\n"
            "}\n"
        )
    except (TypeError, ValueError) as exc:
        if isinstance(exc, SemanticError):
            raise
        raise SylvexError(str(exc)) from exc
