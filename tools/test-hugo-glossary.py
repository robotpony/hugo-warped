#!/usr/bin/env python3
"""Runs glossary/fixtures through the module's glossary partials in Hugo.

    python3 tools/test-hugo-glossary.py [--verbose]

Builds a throwaway site from glossary/fixtures/site with this repo as
its theme and extra.json as the site's added entries. Its home page
writes what entries.html, list.html, index.html, resolve.html and
marks.html return as JSON, each compared with its fixture: entries
without "page", used-in as page paths, marks without line numbers
(Hugo has no line for a page's body). Exits 1 when any differ. Stdlib
only.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FIXTURES = os.path.join(ROOT, "glossary", "fixtures")

HOME = """{{- $a := dict "glossary" "/reference/glossary" "extra" hugo.Data.extra -}}
{{- $entries := slice -}}
{{- range partial "hugo-warped/glossary/entries.html" (dict "glossary" "/reference/glossary") -}}
  {{- $entries = $entries | append (dict "term" .term "also" .also "key" .key "keys" .keys "anchor" .anchor "letter" .letter "def" .def "url" .url) -}}
{{- end -}}
{{- $list := slice -}}
{{- range partial "hugo-warped/glossary/list.html" $a -}}
  {{- $es := slice -}}
  {{- range .entries }}{{ $used := slice }}{{ range .used }}{{ $used = $used | append .File.Path }}{{ end }}{{ $es = $es | append (dict "term" .term "used" $used) }}{{ end -}}
  {{- $list = $list | append (dict "letter" .letter "entries" $es) -}}
{{- end -}}
{{- $resolve := dict -}}
{{- range $t, $_ := hugo.Data.resolve -}}
  {{- $r := partial "hugo-warped/glossary/resolve.html" (merge $a (dict "target" $t)) -}}
  {{- $v := "" }}{{ with $r }}{{ $v = .term }}{{ end -}}
  {{- $resolve = merge $resolve (dict $t $v) -}}
{{- end -}}
{{- $marks := dict -}}
{{- range site.Pages -}}
  {{- if not .File }}{{ continue }}{{ end -}}
  {{- $path := .File.Path -}}
  {{- with partial "hugo-warped/glossary/marks.html" . }}{{ $marks = merge $marks (dict $path .) }}{{ end -}}
{{- end -}}
<pre id="entries">{{ jsonify $entries }}</pre>
<pre id="list">{{ jsonify $list }}</pre>
<pre id="index">{{ jsonify (partial "hugo-warped/glossary/index.html" $a) }}</pre>
<pre id="resolve">{{ jsonify $resolve }}</pre>
<pre id="marks">{{ jsonify $marks }}</pre>
"""


def load(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--hugo", default="hugo")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    site = tempfile.mkdtemp(prefix="hugo-warped-glossary-")
    try:
        shutil.copytree(os.path.join(FIXTURES, "site", "content"), os.path.join(site, "content"))
        os.makedirs(os.path.join(site, "data"))
        os.makedirs(os.path.join(site, "layouts"))
        for name in ("extra", "resolve"):
            shutil.copy(os.path.join(FIXTURES, name + ".json"), os.path.join(site, "data", name + ".json"))
        with open(os.path.join(site, "layouts", "home.html"), "w") as f:
            f.write(HOME)
        for kind in ("section", "page"):
            with open(os.path.join(site, "layouts", kind + ".html"), "w") as f:
                f.write("{{ .Title }}\n")
        with open(os.path.join(site, "hugo.toml"), "w") as f:
            f.write(f'baseURL = "https://example.org/"\ntheme = "{os.path.basename(ROOT)}"\n'
                    f'themesDir = "{os.path.dirname(ROOT)}"\n'
                    'disableKinds = ["taxonomy", "term", "RSS", "sitemap", "robotsTXT"]\n')
        r = subprocess.run([a.hugo, "-s", site, "-d", os.path.join(site, "public")],
                           capture_output=True, text=True)
        if a.verbose or r.returncode:
            print(r.stdout + r.stderr)
        if r.returncode:
            return 1
        with open(os.path.join(site, "public", "index.html"), encoding="utf-8") as f:
            out = f.read()
        got = {k: json.loads(html.unescape(v)) for k, v in re.findall(r'<pre id="(\w+)">(.*?)</pre>', out, re.S)}
        marks = {p: [{"target": m["target"], "text": m["text"]} for m in ms] for p, ms in load("marks.json").items()}
        want = {"entries": load("entries.json"), "list": load("list.json"), "index": load("index.json"),
                "resolve": {k: v or "" for k, v in load("resolve.json").items()}, "marks": marks}
        failed = 0
        entry_pages = [d for d in os.listdir(os.path.join(site, "public", "reference", "glossary"))
                       if os.path.isdir(os.path.join(site, "public", "reference", "glossary", d))]
        if entry_pages:
            failed += 1
            print(f"FAIL  entries render pages of their own: {entry_pages}")
        for k, w in want.items():
            if got.get(k) == w:
                print(f"pass  {k}")
            else:
                failed += 1
                print(f"FAIL  {k}\n  want {json.dumps(w, ensure_ascii=False)}\n  got  {json.dumps(got.get(k), ensure_ascii=False)}")
        print(f"{len(want) + 1 - failed}/{len(want) + 1} pass")
        return 1 if failed else 0
    finally:
        if not a.verbose:
            shutil.rmtree(site)


if __name__ == "__main__":
    sys.exit(main())
