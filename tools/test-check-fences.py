#!/usr/bin/env python3
"""Runs check-fences.py over every fixture in fences/fixtures.

    python3 tools/test-check-fences.py

A block fixture (<type>/<case>.md) must give exactly its .json: the same
type, kind, attributes, lines, fallback and placeholder fields, and the
same warnings by line and code in any order. A page fixture (page/) must
give the same warnings, at their file lines. formula and stack keys come
from fences/fixtures/keys.json, so unknown-token is checked. Stdlib only.
"""
import glob
import importlib.util
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "..", "fences", "fixtures")
spec = importlib.util.spec_from_file_location("check_fences", os.path.join(HERE, "check-fences.py"))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

with open(os.path.join(FIXTURES, "keys.json")) as f:
    KEYS = {k: set(v) for k, v in json.load(f).items() if k in ("formula", "stack")}


def warnings(ws):
    return sorted((w["line"], w["code"]) for w in ws)


class Fixtures(unittest.TestCase):
    def test_blocks(self):
        cases = sorted(glob.glob(os.path.join(FIXTURES, "*", "*.md")))
        self.assertTrue(cases)
        for md in cases:
            if os.path.basename(os.path.dirname(md)) == "page" or md.endswith("README.md"):
                continue
            with self.subTest(case=os.path.relpath(md, FIXTURES)):
                with open(md) as f, open(md[:-3] + ".json") as g:
                    found, page = check.check_page(f.read(), KEYS)
                    want = json.load(g)
                self.assertEqual(len(found), 1)
                self.assertEqual(page, [])
                got = found[0][1].result()
                self.assertEqual(warnings(got.pop("warnings")), warnings(want.pop("warnings")))
                self.assertEqual(got, want)

    def test_pages(self):
        for md in sorted(glob.glob(os.path.join(FIXTURES, "page", "*.md"))):
            with self.subTest(case=os.path.basename(md)):
                with open(md) as f, open(md[:-3] + ".json") as g:
                    found, page = check.check_page(f.read(), KEYS)
                    want = json.load(g)
                got = [(line, code) for line, _, code, _ in check.page_warnings(found, page)]
                self.assertEqual(sorted(got), warnings(want["warnings"]))

    def test_without_keys(self):
        """No keys, no unknown-token: the check is the target's."""
        with open(os.path.join(FIXTURES, "formula", "unknown-token.md")) as f:
            found, _ = check.check_page(f.read())
        self.assertEqual(found[0][1].result()["warnings"], [])


if __name__ == "__main__":
    unittest.main()
