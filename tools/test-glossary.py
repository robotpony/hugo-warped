#!/usr/bin/env python3
"""Runs tools/glossary.py over glossary/fixtures and compares each result.

    python3 tools/test-glossary.py

Checks the entries (without def and url, which are Hugo's), warnings,
marks, link --check, candidates, and the pages after answering yes to
every link question, on a copy of glossary/fixtures/site. Stdlib only.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "glossary.py")
FIXTURES = os.path.join(HERE, "..", "glossary", "fixtures")
SITE = os.path.join(FIXTURES, "site")
CONTENT = os.path.join(SITE, "content")
FOLDER = "reference/glossary"

spec = importlib.util.spec_from_file_location("glossary", TOOL)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def fixture(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return json.load(f) if name.endswith(".json") else f.read()


def run(*args, stdin=None):
    """glossary.py with the fixture site's options (options.txt) added."""
    r = subprocess.run([sys.executable, TOOL, *args, *fixture("options.txt").split()], capture_output=True, text=True, input=stdin)
    return r.returncode, r.stdout


class Glossary(unittest.TestCase):
    def setUp(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.entries, self.warnings = g.load(CONTENT, FOLDER)

    def test_entries(self):
        fields = ("term", "also", "key", "keys", "anchor", "letter")
        want = [{k: e[k] for k in fields} for e in fixture("entries.json")]
        self.assertEqual([{k: e[k] for k in fields} for e in self.entries], want)

    def test_warnings(self):
        key = lambda w: (w["path"], w["code"])
        self.assertEqual(sorted(self.warnings, key=key), sorted(fixture("warnings.json"), key=key))

    def test_resolve(self):
        added = {e["term"] for e in fixture("extra.json")}
        for target, term in fixture("resolve.json").items():
            if term not in added:
                e = g.resolve(self.entries, target)
                self.assertEqual(e and e["term"], term, target)

    def test_marks(self):
        got = {p.path: [{"line": n, "target": t, "text": x} for n, t, x in p.marks()] for p in g.pages(CONTENT)}
        self.assertEqual({k: v for k, v in got.items() if v}, fixture("marks.json"))

    def test_link_check(self):
        code, out = run("link", CONTENT, "--glossary", FOLDER, "--skip", os.path.join(SITE, "skip.txt"), "--check")
        self.assertEqual((code, out), (0, fixture("link-check.txt")))
        code, _ = run("link", CONTENT, "--glossary", FOLDER, "--skip", os.path.join(SITE, "skip.txt"),
                      "--check", "--strict")
        self.assertEqual(code, 1)

    def test_candidates(self):
        self.assertEqual(run("candidates", CONTENT, "--glossary", FOLDER), (0, fixture("candidates.txt")))

    def test_in_context(self):
        line = "one two three four five six seven eight nine ten fond eleven twelve thirteen fourteen fifteen"
        s = line.index("fond")
        got = g.in_context(line, s, s + 4, "[[Fond]]", 40)
        self.assertEqual(got, "…nine ten [[Fond]] eleven twelve…")
        self.assertLessEqual(len(got), 40)
        self.assertEqual(g.in_context("A fond start.", 2, 6, "[[Fond|fond]]", 40), "A [[Fond|fond]] start.")
        self.assertEqual(g.in_context("fond", 0, 4, "[[Fond]]", 40, g.Style(True)),
                         "\x1b[2;32m[[\x1b[0m\x1b[1;32mFond\x1b[0m\x1b[2;32m]]\x1b[0m")

    def test_link_prompt(self):
        env = dict(os.environ, COLUMNS="48")
        r = subprocess.run([sys.executable, TOOL, "link", CONTENT, "--glossary", FOLDER, "--skip",
                            os.path.join(SITE, "skip.txt"), *fixture("options.txt").split()],
                           capture_output=True, text=True, input="s\n" * 50, env=env)
        out = r.stdout.split("\n")
        self.assertNotIn("empty-definition", r.stderr)
        self.assertEqual(out[:6], ["1 stub skipped (not written yet)", "", "Deglaze · 3 pages", "─" * 20, "",
                                   "  1/3  essays/camp-cooking.md:12"])
        self.assertTrue(out[7].startswith("    ") and "[[Deglaze|deglaze]]" in out[7])
        self.assertEqual(out[9:11], ["  y yes  n never here  s skip  q quit › ", "  – skipped"])
        self.assertEqual(out[11:14], ["", "", "  2/3  recipes/dal.md:18"])
        self.assertNotIn("\x1b", r.stdout)
        for line in out:
            if line.startswith("    "):
                self.assertLessEqual(len(line), 48, line)
        self.assertIn("Deglaze: 0 linked, 0 never, 3 skipped", out)
        self.assertIn("Total: 0 linked, 0 never, 8 skipped. Review: git diff", out)

    def test_link_yes(self):
        tmp = tempfile.mkdtemp(prefix="hugo-warped-glossary-")
        try:
            site = os.path.join(tmp, "site")
            shutil.copytree(SITE, site)
            skip = os.path.join(site, "skip.txt")
            run("link", os.path.join(site, "content"), "--glossary", FOLDER, "--skip", skip, stdin="y\n" * 50)
            linked = os.path.join(FIXTURES, "linked")
            for d, _, files in os.walk(os.path.join(site, "content")):
                for name in files:
                    path = os.path.join(d, name)
                    rel = os.path.relpath(path, os.path.join(site, "content"))
                    want = os.path.join(linked, rel) if os.path.exists(os.path.join(linked, rel)) \
                        else os.path.join(CONTENT, rel)
                    with open(path, encoding="utf-8") as a, open(want, encoding="utf-8") as b:
                        self.assertEqual(a.read(), b.read(), rel)
            with open(skip, encoding="utf-8") as a, open(os.path.join(SITE, "skip.txt"), encoding="utf-8") as b:
                self.assertEqual(a.read(), b.read(), "skip.txt")
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
