import unittest
from sylvex_script import SylvexError
from sylvex_compact import compile_source,decode_program,run_compiled
SOURCE='''sylvex 1.0
task build {
 let format = "glb" [obs]
 let triangles = 150000 [rep]
 assert triangles > 0
 if triangles > 100000 { say "high detail" } else { say "optimised" }
 emit {format: format, triangles: triangles}
}
'''
class CompactTests(unittest.TestCase):
 def test_magic(self): self.assertTrue(compile_source(SOURCE).startswith(b"SLXB\\x01"))
 def test_round_trip(self):
  r=run_compiled(compile_source(SOURCE)); self.assertEqual(r["output"],["high detail"]); self.assertTrue(r["compiled"]); self.assertEqual(r["emitted"][0]["format"]["value"],"glb")
 def test_missing_task(self):
  with self.assertRaises(SylvexError): run_compiled(compile_source(SOURCE),"missing")
 def test_bad_magic(self):
  with self.assertRaises(SylvexError): decode_program(b"NOPE\\x01junk")
 def test_bad_version(self):
  with self.assertRaises(SylvexError): decode_program(b"SLXB\\x02junk")
 def test_truncated(self):
  with self.assertRaises(SylvexError): decode_program(b"SLXB\\x01x")
 def test_corrupt(self):
  with self.assertRaises(SylvexError): decode_program(b"SLXB\\x01not-zlib")
 def test_invalid_source(self):
  with self.assertRaises(SylvexError): compile_source("sylvex 1.0\\ntask broken { say unknown }")
if __name__=="__main__": unittest.main()
