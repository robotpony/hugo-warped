#!/usr/bin/env python3
"""Runs tools/check-hugo.sh against a stub Hugo and a throwaway .hugo-version.

    python3 tools/test-check-hugo.py

Stdlib only; never runs a real Hugo.
"""
import os
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check-hugo.sh")
CONFIG = "min = 0.165.0\ntested = 0.169.0\n"
EXTENDED = "v{}+extended+withdeploy darwin/arm64 BuildDate=2026-10-27T14:52:20Z VendorInfo=Homebrew"


class CheckHugo(unittest.TestCase):
    def run_check(self, version="0.169.0", config=CONFIG, line=EXTENDED):
        """(exit code, stderr, stdout). version None means no Hugo on the path."""
        with tempfile.TemporaryDirectory() as site:
            if config is not None:
                with open(os.path.join(site, ".hugo-version"), "w") as f:
                    f.write(config)
            path = "/usr/bin:/bin"
            if version is not None:
                stub = os.path.join(site, "hugo")
                with open(stub, "w") as f:
                    f.write(f"#!/bin/sh\necho 'hugo {line.format(version)}'\n")
                os.chmod(stub, 0o755)
                path = site + ":" + path
            r = subprocess.run(["/bin/bash", SCRIPT], cwd=site, env={"PATH": path},
                               capture_output=True, text=True)
            return r.returncode, r.stderr, r.stdout

    def test_tested_version_is_silent(self):
        self.assertEqual(self.run_check(), (0, "", ""))

    def test_below_min_refuses_and_says_why(self):
        code, err, _ = self.run_check("0.163.0")
        self.assertEqual(code, 1)
        for words in ("0.163.0", "0.165.0", "fallen behind", "brew upgrade hugo"):
            self.assertIn(words, err)

    def test_compares_numerically(self):
        self.assertEqual(self.run_check("0.99.0")[0], 1)
        self.assertEqual(self.run_check("0.170.0", config="min = 0.99\ntested = 0.170\n"), (0, "", ""))

    def test_between_min_and_tested_warns_as_behind(self):
        code, err, _ = self.run_check("0.168.0")
        self.assertEqual(code, 0)
        self.assertIn("warning", err)
        self.assertIn("older than 0.169.0", err)
        self.assertIn("brew upgrade hugo", err)

    def test_newer_than_tested_warns_to_update_the_file(self):
        code, err, _ = self.run_check("0.170.0")
        self.assertEqual(code, 0)
        self.assertIn("newer than 0.169.0", err)
        self.assertIn("tested = 0.170.0", err)

    def test_no_hugo_refuses(self):
        code, err, _ = self.run_check(None)
        self.assertEqual(code, 1)
        self.assertIn("brew install hugo", err)

    def test_extended_only_when_asked(self):
        plain = "v{} darwin/arm64"
        self.assertEqual(self.run_check(line=plain), (0, "", ""))
        code, err, _ = self.run_check(line=plain, config=CONFIG + "extended = true\n")
        self.assertEqual(code, 1)
        self.assertIn("extended", err)
        self.assertEqual(self.run_check(config=CONFIG + "extended = true\n"), (0, "", ""))

    def test_dev_builds_read_as_their_version(self):
        self.assertEqual(self.run_check(line="v{}-DEV+extended darwin/arm64"), (0, "", ""))

    def test_comments_and_blank_lines(self):
        config = "# Pins\n\nmin = 0.165.0  # floor\ntested=0.169.0\n"
        self.assertEqual(self.run_check(config=config), (0, "", ""))

    def test_last_line_without_newline(self):
        self.assertEqual(self.run_check(config="min = 0.165.0\ntested = 0.169.0"), (0, "", ""))

    def test_bad_files_refuse(self):
        for config, words in ((None, "no .hugo-version"),
                              ("tested = 0.169.0\n", "needs min"),
                              ("min = 0.165.0\n", "needs tested"),
                              ("min = new\ntested = 0.169.0\n", "needs min"),
                              (CONFIG + "max = 0.170.0\n", "unknown key"),
                              (CONFIG + "nonsense\n", "can't read"),
                              (CONFIG + "extended = yes\n", "true or false"),
                              ("min = 0.170.0\ntested = 0.169.0\n", "above tested")):
            code, err, _ = self.run_check(config=config)
            self.assertEqual(code, 1, config)
            self.assertIn(words, err)


if __name__ == "__main__":
    unittest.main()
