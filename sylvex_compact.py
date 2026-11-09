"""Sylvex Compact (.slxb) v1 encoder/decoder and runner."""
import json, zlib
from sylvex_script import Interpreter, Node, Parser, SylvexError, VERSION
MAGIC=b"SLXB"; FORMAT_VERSION=1; HEADER=MAGIC+bytes([FORMAT_VERSION]); MAX_UNCOMPRESSED=16*1024*1024

def _pack(value):
    if isinstance(value,Node): return ["N",value.kind,value.value,_pack(value.children),value.line]
    if isinstance(value,tuple): return ["T",*[_pack(x) for x in value]]
    if isinstance(value,list): return ["L",*[_pack(x) for x in value]]
    if value is None or isinstance(value,(str,int,float,bool)): return value
    raise SylvexError(f"Cannot encode AST value {type(value).__name__}")

def _unpack(value, depth=0):
    if depth > 256:
        raise SylvexError("Compact AST nesting limit exceeded")
    if isinstance(value,list):
        if not value: raise SylvexError("Malformed compact AST node")
        if value[0]=="N":
            if len(value)!=5 or not isinstance(value[1],str) or (value[2] is not None and type(value[2]) not in (str,int,float,bool)) or type(value[4]) is not int or value[4]<1:
                raise SylvexError("Malformed compact AST node fields")
            children=_unpack(value[3],depth+1)
            if children is not None and not isinstance(children,(list,tuple)):
                raise SylvexError("Malformed compact AST children")
            return Node(value[1],value[2],children,value[4])
        if value[0]=="T": return tuple(_unpack(x,depth+1) for x in value[1:])
        if value[0]=="L": return [_unpack(x,depth+1) for x in value[1:]]
        raise SylvexError("Unknown compact AST marker")
    if value is None or type(value) in (str,int,bool): return value
    if type(value) is float:
        import math
        if math.isfinite(value): return value
    raise SylvexError("Invalid compact AST scalar")

def compile_source(source):
    tasks=Parser(source).parse()
    payload={"language":"sylvex","language_version":"1.0","compiler_format":FORMAT_VERSION,"runtime_compat":VERSION,"tasks":_pack(tasks)}
    raw=json.dumps(payload,ensure_ascii=False,separators=(",",":"),sort_keys=True).encode("utf-8")
    if len(raw)>MAX_UNCOMPRESSED: raise SylvexError("Compiled program exceeds size limit")
    return HEADER+zlib.compress(raw,level=9)

def decode_program(data):
    if not isinstance(data,bytes) or len(data)<len(HEADER)+2: raise SylvexError("Truncated .slxb file")
    if data[:4]!=MAGIC: raise SylvexError("Not a Sylvex Compact file")
    if data[4]!=FORMAT_VERSION: raise SylvexError(f"Unsupported compact format version {data[4]}")
    try:
        inflater=zlib.decompressobj()
        raw=inflater.decompress(data[5:],MAX_UNCOMPRESSED+1)
        if len(raw)>MAX_UNCOMPRESSED or inflater.unconsumed_tail: raise SylvexError("Compact program exceeds decompression limit")
        raw+=inflater.flush()
        if len(raw)>MAX_UNCOMPRESSED: raise SylvexError("Compact program exceeds decompression limit")
        if not inflater.eof or inflater.unused_data: raise SylvexError("Malformed or trailing compressed data")
        payload=json.loads(raw.decode("utf-8"))
    except SylvexError: raise
    except Exception as exc: raise SylvexError(f"Cannot decode .slxb: {exc}") from exc
    if not isinstance(payload,dict): raise SylvexError("Compact payload must be a JSON object")
    if payload.get("language")!="sylvex" or payload.get("language_version")!="1.0": raise SylvexError("Unsupported Sylvex language version")
    if payload.get("compiler_format")!=FORMAT_VERSION: raise SylvexError("Compact format metadata mismatch")
    if payload.get("runtime_compat")!=VERSION: raise SylvexError(f"Artifact requires runtime {payload.get('runtime_compat')}")
    tasks=_unpack(payload.get("tasks"))
    if not isinstance(tasks,list) or not tasks or any(not isinstance(x,Node) or x.kind!="task" or not isinstance(x.value,str) or not isinstance(x.children,list) for x in tasks): raise SylvexError("Invalid compiled task table")
    payload["tasks"]=tasks
    return payload

def run_compiled(data,task=None,functions=None,max_steps=10000):
    payload=decode_program(data)
    selected=[x for x in payload["tasks"] if task is None or x.value==task]
    if not selected: raise SylvexError(f"Task {task!r} not found")
    if len(selected)!=1: raise SylvexError("Select one task explicitly")
    vm=Interpreter(functions=functions,max_steps=max_steps); vm.block(selected[0].children)
    from sylvex_script import jsonable
    return {"version":VERSION,"task":selected[0].value,"output":vm.output,"emitted":vm.emitted,"variables":{k:jsonable(v) for k,v in vm.env.items()},"steps":vm.steps,"compiled":True}

def compile_file(source_path,output_path):
    data=compile_source(open(source_path,encoding="utf-8").read())
    with open(output_path,"wb") as f: f.write(data)
    return len(data)
