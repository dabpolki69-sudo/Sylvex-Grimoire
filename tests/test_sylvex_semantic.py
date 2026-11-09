import unittest

from sylvex_semantic import (
    SemanticError,
    canonical_json,
    expand_semantic,
    lower_to_slx,
)


SOURCE = """sylvex 0.2
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
"""


class SemanticTests(unittest.TestCase):
    def test_profile_and_values(self):
        properties = expand_semantic(SOURCE)["entities"][0]["properties"]
        self.assertEqual(properties["anatomy"], "biological")
        self.assertEqual(properties["size"], {"value": 2.4, "unit": "m"})
        self.assertEqual(properties["tris"], {"operator": "<=", "value": 150000})
        self.assertEqual(properties["rig+anim"], ["walk", "jump"])
        self.assertEqual(
            properties["steps"]["pipeline"],
            ["model", "rig", "animate", "verify"],
        )

    def test_profile_override(self):
        source = SOURCE.replace(
            " size: 2.4m",
            " material: metal\n size: 2.4m",
        )
        properties = expand_semantic(source)["entities"][0]["properties"]
        self.assertEqual(properties["material"], "metal")

    def test_unknown_profile(self):
        source = "sylvex 0.2\ncreature x @missing {\n size: 2m\n}"
        with self.assertRaises(SemanticError):
            expand_semantic(source)

    def test_duplicate_field(self):
        source = "sylvex 0.2\ncreature x {\n size: 2m\n size: 3m\n}"
        with self.assertRaises(SemanticError):
            expand_semantic(source)

    def test_duplicate_profile(self):
        source = (
            "sylvex 0.2\n"
            "profile p {\n a: 1\n}\n"
            "profile p {\n b: 2\n}\n"
            "creature x @p {\n c: 3\n}"
        )
        with self.assertRaises(SemanticError):
            expand_semantic(source)

    def test_unclosed_block(self):
        with self.assertRaises(SemanticError):
            expand_semantic("sylvex 0.2\ncreature x {\n size: 2m\n")

    def test_canonical_output_is_deterministic(self):
        self.assertEqual(canonical_json(SOURCE), canonical_json(SOURCE))
        self.assertEqual(canonical_json(SOURCE, None), canonical_json(SOURCE, None))

    def test_nested_lists_and_quoted_commas(self):
        source = (
            'sylvex 0.2\n'
            'asset "A, B" {\n'
            ' tags: ["large, creature", walk, [jump, glide]]\n'
            '}'
        )
        expanded = expand_semantic(source)
        self.assertEqual(expanded["entities"][0]["name"], "A, B")
        self.assertEqual(
            expanded["entities"][0]["properties"]["tags"],
            ["large, creature", "walk", ["jump", "glide"]],
        )

    def test_v03_typed_values_and_references(self):
        from sylvex_semantic import relationship_edges

        source = """sylvex 0.3
creature "Sol-Stalker" {
 origin: vec3(1, 2.5, -3)
 accent: color("#00e5ff")
 scale: range(0.8, 1.2)
 rig: ref("rigs/stalker")
}
"""
        expanded = expand_semantic(source)
        props = expanded["entities"][0]["properties"]
        self.assertEqual(expanded["version"], "0.3")
        self.assertEqual(props["origin"], {"$type": "vec3", "x": 1, "y": 2.5, "z": -3})
        self.assertEqual(props["accent"], {"$type": "color", "value": "#00E5FF"})
        self.assertEqual(props["scale"], {"$type": "range", "min": 0.8, "max": 1.2})
        self.assertEqual(props["rig"], {"$ref": "rigs/stalker"})
        self.assertEqual(
            relationship_edges(expanded),
            [{"to": "rigs/stalker", "via": "Sol-Stalker.rig"}],
        )

    def test_v03_rejects_invalid_typed_values(self):
        bad_values = [
            'origin: vec3(1, 2)',
            'accent: color("cyan")',
            'scale: range(2, 1)',
            'rig: ref("")',
            'unknown: mystery(1)',
        ]
        for field in bad_values:
            with self.subTest(field=field):
                source = "sylvex 0.3\ncreature x {\n " + field + "\n}"
                with self.assertRaises(SemanticError):
                    expand_semantic(source)

    def test_lowering_emits_native_map(self):
        from sylvex_script import Interpreter

        result = Interpreter().run(lower_to_slx(SOURCE))
        emitted = result["emitted"][0]["value"]
        self.assertIsInstance(emitted, dict)
        self.assertEqual(emitted["entities"][0]["name"], "Sol-Stalker")
        self.assertEqual(
            emitted["entities"][0]["properties"]["size"],
            {"value": 2.4, "unit": "m"},
        )


if __name__ == "__main__":
    unittest.main()
