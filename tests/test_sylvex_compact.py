import unittest
import json
import zlib

from sylvex_script import SylvexError, VERSION
from sylvex_compact import compile_source, decode_program, run_compiled, HEADER

SOURCE = """sylvex 1.0
task build {
 let format = "glb" [obs]
 let triangles = 150000 [rep]
 assert triangles > 0
 if triangles > 100000 { say "high detail" } else { say "optimised" }
 emit {format: format, triangles: triangles}
}
"""


class CompactTests(unittest.TestCase):
    def test_magic(self):
        self.assertTrue(compile_source(SOURCE).startswith(b"SLXB" + bytes([1])))

    def test_round_trip(self):
        result = run_compiled(compile_source(SOURCE))
        self.assertEqual(result["output"], ["high detail"])
        self.assertTrue(result["compiled"])
        self.assertEqual(result["emitted"][0]["format"]["value"], "glb")

    def test_missing_task(self):
        with self.assertRaises(SylvexError):
            run_compiled(compile_source(SOURCE), "missing")

    def test_bad_magic(self):
        with self.assertRaises(SylvexError):
            decode_program(b"NOPE" + bytes([1]) + b"junk")

    def test_bad_version(self):
        with self.assertRaises(SylvexError):
            decode_program(b"SLXB" + bytes([2]) + b"junk")

    def test_truncated(self):
        with self.assertRaises(SylvexError):
            decode_program(b"SLXB" + bytes([1]) + b"x")

    def test_corrupt(self):
        with self.assertRaises(SylvexError):
            decode_program(b"SLXB" + bytes([1]) + b"not-zlib")

    def test_invalid_source(self):
        with self.assertRaises(SylvexError):
            compile_source("sylvex 1.0\ntask broken { say }")

    def test_decoder_rejects_non_object_payload(self):
        with self.assertRaises(SylvexError):
            decode_program(HEADER + zlib.compress(b"[]"))

    def test_decoder_rejects_malformed_ast_node_fields(self):
        payload = {
            "language": "sylvex",
            "language_version": "1.0",
            "compiler_format": 1,
            "runtime_compat": VERSION,
            "tasks": ["L", ["N", 7, "x", ["L"], 1]],
        }
        data = HEADER + zlib.compress(json.dumps(payload).encode())
        with self.assertRaises(SylvexError):
            decode_program(data)


if __name__ == "__main__":
    unittest.main()
