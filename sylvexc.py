#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
from sylvex_compact import compile_file,decode_program,run_compiled
from sylvex_script import SylvexError

def main(argv=None):
 p=argparse.ArgumentParser(description="Sylvex Compact compiler and runner")
 sub=p.add_subparsers(dest="command",required=True)
 c=sub.add_parser("compile"); c.add_argument("source"); c.add_argument("-o","--output")
 r=sub.add_parser("run"); r.add_argument("file"); r.add_argument("--task"); r.add_argument("--json",action="store_true"); r.add_argument("--max-steps",type=int,default=10000)
 i=sub.add_parser("info"); i.add_argument("file")
 a=p.parse_args(argv)
 try:
  if a.command=="compile":
   out=a.output or str(Path(a.source).with_suffix(".slxb")); size=compile_file(a.source,out); print(f"Compiled {a.source} -> {out} ({size} bytes)")
  elif a.command=="run":
   result=run_compiled(Path(a.file).read_bytes(),a.task,max_steps=a.max_steps)
   if a.json: print(json.dumps(result,ensure_ascii=False,indent=2))
   else:
    for line in result["output"]: print(line)
    for item in result["emitted"]: print(json.dumps(item,ensure_ascii=False))
  else:
   payload=decode_program(Path(a.file).read_bytes())
   print(json.dumps({"format":"SLXB","format_version":1,"language":payload["language"],"language_version":payload["language_version"],"runtime_compat":payload["runtime_compat"],"tasks":[x.value for x in payload["tasks"]],"bytes":Path(a.file).stat().st_size},indent=2))
 except (OSError,SylvexError) as exc: print(f"Sylvex Compact error: {exc}",file=sys.stderr); return 1
 return 0
if __name__=="__main__": raise SystemExit(main())
