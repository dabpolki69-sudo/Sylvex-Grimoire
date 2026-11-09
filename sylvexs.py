#!/usr/bin/env python3
import argparse,sys
from pathlib import Path
from sylvex_semantic import SemanticError,canonical_json,lower_to_slx
def main(argv=None):
 p=argparse.ArgumentParser(description="Sylvex 0.2 semantic expander")
 p.add_argument("file"); p.add_argument("--lower"); p.add_argument("--compact",action="store_true"); a=p.parse_args(argv)
 try:
  src=Path(a.file).read_text(encoding="utf-8")
  if a.lower: Path(a.lower).write_text(lower_to_slx(src),encoding="utf-8"); print(f"Lowered to {a.lower}")
  else: print(canonical_json(src,None if a.compact else 2))
 except (OSError,SemanticError) as e: print(f"Sylvex semantic error: {e}",file=sys.stderr); return 1
 return 0
if __name__=="__main__": raise SystemExit(main())
