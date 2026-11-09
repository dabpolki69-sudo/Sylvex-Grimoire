import unittest
from sylvex_semantic import SemanticError,canonical_json,expand_semantic,lower_to_slx
SOURCE='''sylvex 0.2
profile realistic {
 anatomy: biological
 material: pbr
 motion: natural
 verify: anatomy+rig+animation
}
creature "Sol-Stalker" @realistic {
 size: 2.4m
 tris: <=150k
 rig+anim: walk,jump
 steps: model>rig>animate>verify
}
'''
class SemanticTests(unittest.TestCase):
 def test_profile_and_values(self):
  p=expand_semantic(SOURCE)["entities"][0]["properties"]
  self.assertEqual(p["anatomy"],"biological"); self.assertEqual(p["size"],{"value":2.4,"unit":"m"})
  self.assertEqual(p["tris"],{"operator":"<=","value":150000}); self.assertEqual(p["rig+anim"],["walk","jump"])
  self.assertEqual(p["steps"]["pipeline"],["model","rig","animate","verify"])
 def test_override(self):
  s=SOURCE.replace(' size: 2.4m',' material: metal\n size: 2.4m')
  self.assertEqual(expand_semantic(s)["entities"][0]["properties"]["material"],"metal")
 def test_unknown_profile(self):
  with self.assertRaises(SemanticError): expand_semantic("sylvex 0.2\ncreature x @missing {\n size: 2m\n}")
 def test_duplicate_field(self):
  with self.assertRaises(SemanticError): expand_semantic("sylvex 0.2\ncreature x {\n size: 2m\n size: 3m\n}")
 def test_unclosed(self):
  with self.assertRaises(SemanticError): expand_semantic("sylvex 0.2\ncreature x {\n size: 2m\n")
 def test_canonical(self): self.assertEqual(canonical_json(SOURCE),canonical_json(SOURCE))
 def test_lowering(self):
  from sylvex_script import Interpreter
  r=Interpreter().run(lower_to_slx(SOURCE))
  self.assertEqual(r["emitted"][0]["value"]["entities"][0]["name"],"Sol-Stalker")
if __name__=="__main__": unittest.main()
