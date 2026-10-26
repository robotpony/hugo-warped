#!/usr/bin/env python3
"""Runs the fence fixtures through the module's parse partials in Hugo.

    python3 tools/test-hugo-partials.py
    python3 tools/test-hugo-partials.py --types table,formula --verbose

Builds one throwaway site with this repo as its theme and one page per
block fixture (fences/fixtures/<type>/<case>.md). The site's only hook,
render-codeblock.html, calls hugo-warped/parse.html with the keys from
fences/fixtures/keys.json and writes the parse as JSON, so each case is
compared with its .json in full, as tools/test-check-fences.py does for
the validator. Warnings compare by line and code, in any order. The
bad-attributes cases are skipped: Hugo parses the {…} group before a
hook sees it. Exits 1 when any case fails. Stdlib only.
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FIXTURES = os.path.join(ROOT, "fences", "fixtures")
SKIP = {"table/bad-attributes"}

HOOK = """{{- $keys := dict -}}
{{- range $k, $v := hugo.Data.fencekeys }}{{ if reflect.IsSlice $v }}{{ $keys = merge $keys (dict $k $v) }}{{ end }}{{ end -}}
{{- with partial "hugo-warped/parse.html" (dict "hook" . "keys" $keys) -}}
<pre class="parse">{{ jsonify . }}</pre>
{{- end -}}
"""


def warnings(ws):
    return sorted((w["line"], w["code"]) for w in ws)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--types", help="comma-separated fixture types (default: all)")
    ap.add_argument("--hugo", default="hugo")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    types = a.types.split(",") if a.types else sorted(
        d for d in os.listdir(FIXTURES) if os.path.isdir(os.path.join(FIXTURES, d)) and d != "page")

    site = tempfile.mkdtemp(prefix="hugo-warped-partials-")
    try:
        for d in ("content", "data", "layouts/_default/_markup"):
            os.makedirs(os.path.join(site, d))
        with open(os.path.join(site, "hugo.toml"), "w") as f:
            f.write(f'baseURL = "https://example.org/"\ntheme = "{os.path.basename(ROOT)}"\n'
                    f'themesDir = "{os.path.dirname(ROOT)}"\n'
                    'disableKinds = ["taxonomy", "term", "RSS", "sitemap", "robotsTXT", "home", "section"]\n')
        shutil.copy(os.path.join(FIXTURES, "keys.json"), os.path.join(site, "data", "fencekeys.json"))
        with open(os.path.join(site, "layouts", "_default", "single.html"), "w") as f:
            f.write("{{ .Content }}")
        with open(os.path.join(site, "layouts", "_default", "_markup", "render-codeblock.html"), "w") as f:
            f.write(HOOK)
        cases = []
        for t in types:
            for md in sorted(glob.glob(os.path.join(FIXTURES, t, "*.md"))):
                case = f"{t}/{os.path.basename(md)[:-3]}"
                if case in SKIP:
                    continue
                slug = case.replace("/", "-")
                with open(md) as src, open(os.path.join(site, "content", slug + ".md"), "w") as dst:
                    dst.write(f"---\ntitle: {slug}\nslug: {slug}\n---\n" + src.read())
                cases.append((case, slug))
        r = subprocess.run([a.hugo, "-s", site, "-d", os.path.join(site, "public")],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if r.returncode:
            print(r.stdout + r.stderr)
            sys.exit(f"hugo failed ({r.returncode})")

        fails = 0
        for case, slug in cases:
            with open(os.path.join(FIXTURES, case + ".json")) as f:
                want = json.load(f)
            page = os.path.join(site, "public", slug, "index.html")
            found = re.findall(r'<pre class="parse">(.*?)</pre>', open(page).read() if os.path.exists(page) else "", re.S)
            if len(found) != 1:
                fails += 1
                print(f"FAIL {case}: {len(found)} parses")
                continue
            got = json.loads(html.unescape(found[0]))
            problems = []
            if warnings(got.pop("warnings", [])) != warnings(want.pop("warnings")):
                problems.append("warnings")
            for k in sorted(set(got) | set(want)):
                if got.get(k, "∅") != want.get(k, "∅"):
                    problems.append(k)
            if problems:
                fails += 1
                print(f"FAIL {case}: {', '.join(problems)}")
                if a.verbose:
                    for k in problems:
                        if k != "warnings":
                            print(f"  got  {k}: {json.dumps(got.get(k), ensure_ascii=False)}\n  want {k}: {json.dumps(want.get(k), ensure_ascii=False)}")
            elif a.verbose:
                print(f"ok   {case}")
        print(f"{len(cases) - fails}/{len(cases)} pass")
        sys.exit(1 if fails else 0)
    finally:
        shutil.rmtree(site)


if __name__ == "__main__":
    main()
