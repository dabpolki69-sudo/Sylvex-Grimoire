#!/usr/bin/env python3
"""Sylvex Script 0.1 reference interpreter. MIT License."""
import argparse, json, re, sys
from dataclasses import dataclass
from pathlib import Path

VERSION="0.1.0"
EVIDENCE={"obs","rep","inf","hyp","cit","pre","ctrl","fail","unk","rej","nov"}
class SylvexError(Exception): pass
@dataclass
class Token: kind:str; value:object; line:int; col:int
@dataclass
class Node: kind:str; value:object=None; children:list=None; line:int=0
@dataclass
class Evidenced: value:object; evidence:str=None
TOKEN=re.compile(r'''(?P<WS>[ \t\r]+)|(?P<NL>\n)|(?P<COMMENT>\#[^\n]*)|(?P<STR>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(?P<NUM>\d+(?:\.\d+)?)|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)|(?P<OP>==|!=|<=|>=|[{}()\[\],:+*/%<>=-])''')
def lex(src):
    out=[]; p=0; line=1; col=1
    while p<len(src):
        m=TOKEN.match(src,p)
        if not m: raise SylvexError(f"Unexpected character {src[p]!r} at {line}:{col}")
        k,r=m.lastgroup,m.group()
        if k not in ("WS","COMMENT"):
            if k=="NL": out.append(Token(k,"\\n",line,col)); line+=1; col=1
            else:
                v=r
                if k=="STR":
                    try: v=json.loads(r) if r[0]=='"' else bytes(r[1:-1],"utf8").decode("unicode_escape")
                    except Exception as e: raise SylvexError(f"Bad string at {line}:{col}: {e}")
                elif k=="NUM": v=float(r) if "." in r else int(r)
                out.append(Token(k,v,line,col))
        if k!="NL": col+=len(r)
        p=m.end()
    out.append(Token("EOF",None,line,col)); return out
class Parser:
    prec={"or":1,"and":2,"==":3,"!=":3,"<":3,">":3,"<=":3,">=":3,"+":4,"-":4,"*":5,"/":5,"%":5}
    def __init__(self,s): self.ts=lex(s); self.i=0
    def peek(self): return self.ts[self.i]
    def pop(self): t=self.peek(); self.i+=1; return t
    def accept(self,v):
        if self.peek().value==v: return self.pop()
    def need(self,v):
        if not self.accept(v): self.err(f"Expected {v!r}")
    def err(self,msg): t=self.peek(); raise SylvexError(f"{msg} at {t.line}:{t.col}")
    def ident(self):
        t=self.pop()
        if t.kind!="ID": self.err("Expected identifier")
        return t.value
    def lines(self):
        while self.peek().kind=="NL": self.pop()
    def block(self):
        self.need("{"); self.lines(); a=[]
        while self.peek().value!="}":
            if self.peek().kind=="EOF": self.err("Unclosed block")
            a.append(self.stmt()); self.lines()
        self.pop(); return a
    def stmt(self):
        t=self.pop()
        if t.kind!="ID": self.err("Expected statement")
        if t.value=="task": return Node("task",self.ident(),self.block(),t.line)
        if t.value in ("let","set"):
            name=self.ident(); self.need("="); e=self.expr(); tag=None
            if self.accept("["):
                tag=self.ident(); self.need("]")
                if tag not in EVIDENCE: self.err(f"Unknown evidence tag {tag!r}")
            return Node(t.value,name,[e,tag],t.line)
        if t.value in ("say","emit","assert"): return Node(t.value,children=[self.expr()],line=t.line)
        if t.value=="call":
            name=self.ident(); self.need("("); args=[]
            if self.peek().value!=")":
                args.append(self.expr())
                while self.accept(","): args.append(self.expr())
            self.need(")"); return Node("call",name,args,t.line)
        if t.value=="if":
            cond=self.expr(); yes=self.block(); self.lines(); no=self.block() if self.accept("else") else []
            return Node("if",children=[cond,yes,no],line=t.line)
        self.err(f"Unknown statement {t.value!r}")
    def expr(self,minp=0):
        t=self.pop()
        if t.kind in ("NUM","STR"): left=Node("lit",t.value,line=t.line)
        elif t.kind=="ID" and t.value in ("true","false","null"): left=Node("lit",{"true":True,"false":False,"null":None}[t.value],line=t.line)
        elif t.kind=="ID" and t.value=="not": left=Node("unary","not",[self.expr(6)],t.line)
        elif t.kind=="OP" and t.value in ("-","+"): left=Node("unary",t.value,[self.expr(6)],t.line)
        elif t.kind=="ID": left=Node("name",t.value,line=t.line)
        elif t.value=="(":
            left=self.expr(); self.need(")")
        elif t.value=="[":
            vals=[]
            if self.peek().value!="]":
                vals.append(self.expr())
                while self.accept(","): vals.append(self.expr())
            self.need("]"); left=Node("list",children=vals,line=t.line)
        elif t.value=="{":
            pairs=[]
            if self.peek().value!="}":
                while True:
                    k=self.expr(); self.need(":"); v=self.expr(); pairs.append((k,v))
                    if not self.accept(","): break
            self.need("}"); left=Node("map",children=pairs,line=t.line)
        else: self.err("Expected expression")
        while self.peek().value in self.prec and self.prec[self.peek().value]>=minp:
            op=self.pop().value; right=self.expr(self.prec[op]+1); left=Node("bin",op,[left,right],t.line)
        return left
    def parse(self):
        self.lines(); self.need("sylvex"); v=self.pop()
        if v.kind not in ("NUM","STR") or str(v.value)!="1.0": self.err("Only sylvex 1.0 is supported")
        self.lines(); tasks=[]
        while self.peek().kind!="EOF": tasks.append(self.stmt()); self.lines()
        if not tasks or any(x.kind!="task" for x in tasks): self.err("Program must contain task declarations")
        return tasks
def plain(v): return v.value if isinstance(v,Evidenced) else v
def jsonable(v):
    if isinstance(v,Evidenced): return {"value":jsonable(v.value),"evidence":v.evidence}
    if isinstance(v,dict): return {str(k):jsonable(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [jsonable(x) for x in v]
    if v is None or isinstance(v,(str,int,float,bool)): return v
    raise SylvexError(f"Cannot export {type(v).__name__} to JSON")
class Interpreter:
    def __init__(self,functions=None,max_steps=10000):
        self.functions=dict(functions or {}); self.max_steps=max_steps; self.steps=0; self.env={}; self.output=[]; self.emitted=[]
    def tick(self,line):
        self.steps+=1
        if self.steps>self.max_steps: raise SylvexError(f"Step limit exceeded near line {line}")
    def ev(self,n):
        if n.kind=="lit": return n.value
        if n.kind=="name":
            if n.value not in self.env: raise SylvexError(f"Undefined variable {n.value!r} at line {n.line}")
            return self.env[n.value]
        if n.kind=="list": return [self.ev(x) for x in n.children]
        if n.kind=="map": return {plain(self.ev(k)):self.ev(v) for k,v in n.children}
        if n.kind=="unary":
            v=plain(self.ev(n.children[0])); return not v if n.value=="not" else (-v if n.value=="-" else +v)
        if n.kind=="bin":
            a,b=(plain(self.ev(x)) for x in n.children); op=n.value
            funcs={"+":lambda:a+b,"-":lambda:a-b,"*":lambda:a*b,"/":lambda:a/b,"%":lambda:a%b,"==":lambda:a==b,"!=":lambda:a!=b,"<":lambda:a<b,">":lambda:a>b,"<=":lambda:a<=b,">=":lambda:a>=b,"and":lambda:bool(a and b),"or":lambda:bool(a or b)}
            try: return funcs[op]()
            except (TypeError,ZeroDivisionError) as e: raise SylvexError(f"Invalid operation at line {n.line}: {e}")
        raise SylvexError("Invalid expression")
    def block(self,body):
        for n in body:
            self.tick(n.line)
            if n.kind in ("let","set"):
                exists=n.value in self.env
                if n.kind=="let" and exists: raise SylvexError(f"Variable {n.value!r} already declared")
                if n.kind=="set" and not exists: raise SylvexError(f"Cannot set undeclared variable {n.value!r}")
                self.env[n.value]=Evidenced(plain(self.ev(n.children[0])),n.children[1])
            elif n.kind=="say": self.output.append(str(plain(self.ev(n.children[0]))))
            elif n.kind=="emit": self.emitted.append(jsonable(self.ev(n.children[0])))
            elif n.kind=="assert":
                if not self.ev(n.children[0]): raise SylvexError(f"Assertion failed at line {n.line}")
            elif n.kind=="if": self.block(n.children[1] if self.ev(n.children[0]) else n.children[2])
            elif n.kind=="call":
                if n.value not in self.functions: raise SylvexError(f"Function {n.value!r} is not allowlisted")
                try: result=self.functions[n.value](*[plain(self.ev(x)) for x in n.children])
                except Exception as e: raise SylvexError(f"Host function {n.value!r} failed: {e}")
                self.env["_last"]=Evidenced(result,"obs")
    def run(self,source,task=None):
        tasks=Parser(source).parse(); selected=[t for t in tasks if task is None or t.value==task]
        if not selected: raise SylvexError(f"Task {task!r} not found")
        if len(selected)>1: raise SylvexError("Select a task with --task")
        self.block(selected[0].children)
        return {"version":VERSION,"task":selected[0].value,"output":self.output,"emitted":self.emitted,"variables":{k:jsonable(v) for k,v in self.env.items()},"steps":self.steps}
def main(argv=None):
    p=argparse.ArgumentParser(description="Sylvex Script 0.1 interpreter"); p.add_argument("file"); p.add_argument("--task"); p.add_argument("--json",action="store_true"); p.add_argument("--max-steps",type=int,default=10000); a=p.parse_args(argv)
    try:
        r=Interpreter(max_steps=a.max_steps).run(Path(a.file).read_text(encoding="utf8"),a.task)
        if a.json: print(json.dumps(r,ensure_ascii=False,indent=2))
        else:
            for x in r["output"]: print(x)
            for x in r["emitted"]: print(json.dumps(x,ensure_ascii=False))
    except (OSError,SylvexError) as e: print(f"Sylvex error: {e}",file=sys.stderr); return 1
    return 0
if __name__=="__main__": raise SystemExit(main())
