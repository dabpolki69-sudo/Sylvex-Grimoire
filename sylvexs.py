#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from sylvex_semantic import (
    SemanticError,
    canonical_json,
    expand_semantic,
    lower_to_slx,
    validate_semantic,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sylvex 0.2/0.3 semantic expander and validator")
    parser.add_argument("file")
    parser.add_argument("--lower", metavar="OUTPUT")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--validate", action="store_true", help="validate entity identifiers and document structure")
    parser.add_argument("--known-ref", action="append", default=[], metavar="ID", help="declare a reference as resolvable; repeat as needed")
    parser.add_argument("--strict-refs", action="store_true", help="fail if any ref() is not in the supplied --known-ref registry")
    args = parser.parse_args(argv)

    try:
        source = Path(args.file).read_text(encoding="utf-8")
        if args.lower:
            if args.validate or args.strict_refs or args.known_ref:
                raise SemanticError("--lower cannot be combined with validation options")
            Path(args.lower).write_text(lower_to_slx(source), encoding="utf-8")
            print(f"Lowered to {args.lower}")
            return 0

        if args.validate or args.strict_refs or args.known_ref:
            expanded = expand_semantic(source)
            report = validate_semantic(
                expanded,
                known_refs=args.known_ref if args.known_ref or args.strict_refs else None,
                strict_refs=args.strict_refs,
            )
            print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=None if args.compact else 2))
            return 0

        print(canonical_json(source, None if args.compact else 2))
    except (OSError, SemanticError) as exc:
        print(f"Sylvex semantic error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
