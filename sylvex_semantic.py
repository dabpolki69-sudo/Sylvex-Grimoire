"""Sylvex 0.2 semantic shorthand parser and deterministic expander."""
import json,re
from dataclasses import dataclass,field
class SemanticError(ValueError): pass
_HEADER=re.compile(r"^sylvex\s+0\.2$")
_PROFILE=re.compile(r"^profile\s+([A-Za-z_][\w-]*)\s*\{$")
_ENTITY=re.compile(r'^([A-Za-z_][\w-]*)\s+(.+?)(?:\s+@([A-Za-z_][\w-]*))?\s*\{$')
_KEY=re.compile(r"^([A-Za-z_][\w+.-]*)\s*:\s*(.*?)$")
_PIPE=re.compile(r"^[A-Za-z_][\w-]*(?:\s*>\s*[A-Za-z_][\w-]*)+$")
_CONSTRAINT=re.compile(r"^(<=|>=|<|>|==|!=)\s*(.+)$")
_QUANTITY=re.compile(r"^(\d+(?:\.\d+)?)(k|m)?\s*([A-Za-z][\w/^.-]*)?$",re.I)
@dataclass
class Declaration:
 kind:str
 name:str
 profile:str|None
 fields:dict=field(default_factory=dict)
 line:int=0
def _scalar(raw,line):
 raw=raw.strip()
 if not raw: raise SemanticError(f"Empty value at line {line}")
 if raw[0] in "\"'" and raw[-1:]==raw[0]:
  try: return json.loads(raw) if raw[0]=='"' else raw[1:-1]
  except Exception as e: raise SemanticError(f"Invalid string at line {line}: {e}")
 if raw in ("true","false","null"): return {"true":True,"false":False,"null":None}[raw]
 if _PIPE.fullmatch(raw): return {"pipeline":[x.strip() for x in raw.split(">")]}
 if raw.startswith("[") and raw.endswith("]"):
  inner=raw[1:-1].strip(); return [] if not inner else [_scalar(x,line) for x in inner.split(",")]
 m=_CONSTRAINT.fullmatch(raw)
 if m: return {"operator":m.group(1),"value":_scalar(m.group(2),line)}
 if "," in raw or "+" in raw:
  sep="," if "," in raw else "+"; return [_scalar(x,line) for x in raw.split(sep)]
 m=_QUANTITY.fullmatch(raw)
 if m:
  n=float(m.group(1)) if "." in m.group(1) else int(m.group(1))
  if m.group(2)=="k": n*=1000
  elif m.group(2)=="m": n*=1000000
  return {"value":n,"unit":m.group(3)} if m.group(3) else n
 if re.fullmatch(r"-?\d+(?:\.\d+)?",raw): return float(raw) if "." in raw else int(raw)
 if re.fullmatch(r"[A-Za-z_][\w-]*",raw): return raw
 raise SemanticError(f"Cannot parse value {raw!r} at line {line}")
def parse_semantic(source):
 lines=source.splitlines()
 if not lines or not _HEADER.fullmatch(lines[0].strip()): raise SemanticError("Semantic source must begin with 'sylvex 0.2'")
 profiles={}; declarations=[]; cur=None
 for no,raw in enumerate(lines[1:],2):
  line=raw.strip()
  if not line or line.startswith("#"): continue
  if line=="}":
   if cur is None: raise SemanticError(f"Unexpected closing brace at line {no}")
   if cur.kind=="profile":
    if cur.name in profiles: raise SemanticError(f"Duplicate profile {cur.name!r}")
    profiles[cur.name]=cur.fields
   else: declarations.append(cur)
   cur=None; continue
  if cur is None:
   m=_PROFILE.fullmatch(line)
   if m: cur=Declaration("profile",m.group(1),None,line=no); continue
   m=_ENTITY.fullmatch(line)
   if m:
    label=m.group(2).strip()
    if label.startswith('"'):
     try: label=json.loads(label)
     except Exception as e: raise SemanticError(f"Invalid entity name at line {no}: {e}")
    elif not re.fullmatch(r"[A-Za-z_][\w-]*",label): raise SemanticError(f"Entity name must be identifier or quoted string at line {no}")
    cur=Declaration(m.group(1),label,m.group(3),line=no); continue
   raise SemanticError(f"Expected profile or entity declaration at line {no}")
  m=_KEY.fullmatch(line)
  if not m: raise SemanticError(f"Expected key: value at line {no}")
  key,val=m.groups()
  if key in cur.fields: raise SemanticError(f"Duplicate field {key!r} at line {no}")
  cur.fields[key]=_scalar(val,no)
 if cur is not None: raise SemanticError(f"Unclosed {cur.kind} block starting at line {cur.line}")
 if not declarations: raise SemanticError("Program must declare at least one semantic entity")
 for d in declarations:
  if d.profile and d.profile not in profiles: raise SemanticError(f"Unknown profile @{d.profile} at line {d.line}")
 return profiles,declarations
def expand_semantic(source):
 profiles,declarations=parse_semantic(source); entities=[]
 for d in declarations:
  props=dict(profiles.get(d.profile,{})); props.update(d.fields)
  entities.append({"kind":d.kind,"name":d.name,"profile":d.profile,"profile_version":"0.2","properties":props})
 return {"language":"sylvex","version":"0.2","profiles":profiles,"entities":entities}
def canonical_json(source,indent=2): return json.dumps(expand_semantic(source),ensure_ascii=False,sort_keys=True,indent=indent)
def lower_to_slx(source):
 from sylvex_script import SylvexError
 try:
  literal=json.dumps(expand_semantic(source),ensure_ascii=False,separators=(",",":"))
  return "sylvex 1.0\ntask semantic_expansion {\n let specification = "+literal+"\n emit specification\n}\n"
 except (TypeError,ValueError) as e:
  if isinstance(e,SemanticError): raise
  raise SylvexError(str(e)) from e
