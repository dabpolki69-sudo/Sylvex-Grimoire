import unittest
from sylvex_script import Interpreter, SylvexError
class Tests(unittest.TestCase):
 def runslx(self,s,**kw): return Interpreter(**kw).run("sylvex 1.0\n"+s)
 def test_hello(self): self.assertEqual(self.runslx('task t { say "hello" }')["output"],["hello"])
 def test_evidence(self): self.assertEqual(self.runslx('task t { let x = 42 [obs] emit x }')["emitted"],[{"value":42,"evidence":"obs"}])
 def test_math(self): self.assertEqual(self.runslx('task t { let x = 2 + 3 * 4 assert x == 14 emit x }')["emitted"][0]["value"],14)
 def test_if(self): self.assertEqual(self.runslx('task t { let x = 3 if x > 2 { say "yes" } else { say "no" } }')["output"],["yes"])
 def test_set_undeclared(self):
  with self.assertRaises(SylvexError): self.runslx('task t { set x = 2 }')
 def test_unknown_name(self):
  with self.assertRaises(SylvexError): self.runslx('task t { say missing }')
 def test_allowlisted_host(self): self.assertEqual(self.runslx('task t { call twice(21) emit _last }',functions={"twice":lambda x:x*2})["emitted"][0]["value"],42)
 def test_host_denied(self):
  with self.assertRaises(SylvexError): self.runslx('task t { call shell("id") }')
 def test_limit(self):
  with self.assertRaises(SylvexError): Interpreter(max_steps=1).run('sylvex 1.0\ntask t { let x = 1 say x }')
 def test_version(self):
  with self.assertRaises(SylvexError): Interpreter().run('sylvex 2.0\ntask t { say 1 }')
if __name__=="__main__": unittest.main()
