"""Reproducible byte-count comparison; representations are not semantically interchangeable."""
import json
from pathlib import Path
from sylvex_compact import compile_source
root=Path(__file__).resolve().parent.parent
slx=(root/"examples"/"evidence.slx").read_text(encoding="utf-8")
py='''asset = {"format": "glb", "triangles": 150000, "realism": "hyp"}
assert asset["triangles"] > 0
print(asset)
'''
js=json.dumps({"task":"evidence_demo","format":{"value":"glb","evidence":"obs"},"triangles":{"value":150000,"evidence":"rep"},"realism":{"value":True,"evidence":"hyp"}},separators=(",",":"))
rows={"Sylvex source (.slx)":len(slx.encode()),"Sylvex compact (.slxb)":len(compile_source(slx)),"Python source":len(py.encode()),"JSON data":len(js.encode())}
print("Bytes (lower is smaller; semantics differ by representation):")
for name,size in rows.items(): print(f"{name:26} {size:6} bytes")
print(json.dumps(rows,indent=2))
