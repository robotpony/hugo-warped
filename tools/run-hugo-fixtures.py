#!/usr/bin/env python3
"""Run the fence fixtures through a Hugo theme's code-block hooks.

    tools/run-hugo-fixtures.py ~/projects/sites/w42/themes/w42
    tools/run-hugo-fixtures.py <theme> --types tabs --verbose

Each fixture (fences/fixtures/<type>/<case>.md) becomes one page of a
throwaway Hugo site that uses the theme. One build, then each case is
compared with its <case>.json:

- warnings, by code and line (the opening fence is line 1), read from
  Hugo's WARN lines in the form `<type> [<code>]: ... in "<file>:<line>:<col>"`;
- fallback: true when nothing was drawn (no item elements in the page);
- when not a fallback, how many items were drawn: one per year or row in
  `lines` for diagram types, one per `tab` keyword for tabs;
- for tabs, each panel's label against its `value`, as rendered text.

Item and label elements are found by class, w42's by default; a theme
that names them differently passes --item TYPE=CLASS and --label
TYPE=CLASS. Exits 1 when any case fails. Stdlib only.
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

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fences", "fixtures")
ITEMS = {"timeline": "tline-mark", "flow": "flow-step", "tabs": "tabs-panel"}
LABELS = {"tabs": "tabs-label"}


def pairs(values, defaults):
    out = dict(defaults)
    for v in values or []:
        k, _, c = v.partition("=")
        out[k] = c
    return out


def plain(md):
    """A label's text once rendered: links and images by their text, no emphasis or code marks."""
    md = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", md)
    return re.sub(r"[*_`]", "", md).strip()


def expected_items(t, exp):
    if t == "tabs":
        return [l for l in exp["lines"] if l.get("keyword") == "tab"]
    return [l for l in exp["lines"] if "row" in l or "year" in l]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("theme", help="path to the theme's folder")
    ap.add_argument("--types", default="timeline,flow,tabs", help="comma-separated fixture types")
    ap.add_argument("--item", action="append", metavar="TYPE=CLASS", help="class of one drawn item")
    ap.add_argument("--label", action="append", metavar="TYPE=CLASS", help="class of a panel label")
    ap.add_argument("--hugo", default="hugo")
    ap.add_argument("--verbose", action="store_true", help="print passing cases and Hugo's errors")
    a = ap.parse_args()
    theme = os.path.abspath(os.path.expanduser(a.theme))
    items, labels = pairs(a.item, ITEMS), pairs(a.label, LABELS)
    fm = "---\ntitle: {0}\nslug: {0}\n---\n"
    offset = fm.count("\n")  # front matter lines before the fence

    site = tempfile.mkdtemp(prefix="fence-fixtures-")
    try:
        os.makedirs(os.path.join(site, "content"))
        with open(os.path.join(site, "hugo.toml"), "w") as f:
            f.write(f'baseURL = "https://example.org/"\ntheme = "{os.path.basename(theme)}"\n'
                    f'themesDir = "{os.path.dirname(theme)}"\n'
                    'disableKinds = ["taxonomy", "term", "RSS", "sitemap", "robotsTXT"]\n')
        cases = []
        for t in a.types.split(","):
            folder = os.path.join(FIXTURES, t)
            for name in sorted(os.listdir(folder)):
                if not name.endswith(".md"):
                    continue
                case, slug = name[:-3], f"{t}-{name[:-3]}"
                with open(os.path.join(folder, name)) as src, \
                        open(os.path.join(site, "content", slug + ".md"), "w") as dst:
                    dst.write(fm.format(slug) + src.read())
                cases.append((t, case, slug))
        out = os.path.join(site, "public")
        r = subprocess.run([a.hugo, "-s", site, "-d", out], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL)
        log = r.stdout + r.stderr
        if r.returncode:
            print(log)
            sys.exit(f"hugo failed ({r.returncode})")
        if a.verbose:
            print("\n".join(l for l in log.splitlines() if "ERROR" in l))

        fails = 0
        for t, case, slug in cases:
            with open(os.path.join(FIXTURES, t, case + ".json")) as f:
                exp = json.load(f)
            # A set: Hugo can render a page twice and repeat its warnings (fences/README.md).
            got = sorted({(int(m.group(2)) - offset, m.group(1)) for m in re.finditer(
                r"WARN\s+\w+ \[([a-z-]+)\]:.*?/" + re.escape(slug) + r"\.md:(\d+):\d+", log)})
            want = sorted((w["line"], w["code"]) for w in exp["warnings"])
            page = os.path.join(out, slug, "index.html")
            doc = open(page).read() if os.path.exists(page) else ""
            drawn = len(re.findall(r'class="%s[" ]' % re.escape(items[t]), doc))
            problems = []
            if got != want:
                problems.append(f"warnings {got}, want {want}")
            if (drawn == 0) != exp["fallback"]:
                problems.append(f"fallback {drawn == 0}, want {exp['fallback']}")
            wanted = expected_items(t, exp)
            if not exp["fallback"] and drawn != len(wanted):
                problems.append(f"{drawn} drawn, want {len(wanted)}")
            if t in labels and not exp["fallback"]:
                seen = [html.unescape(re.sub(r"<[^>]+>", "", m)).strip() for m in re.findall(
                    r'class="%s"[^>]*>(.*?)</(?:label|div)>' % re.escape(labels[t]), doc, re.S)]
                if seen != [plain(l["value"]) for l in wanted]:
                    problems.append(f"labels {seen}, want {[plain(l['value']) for l in wanted]}")
            if problems:
                fails += 1
                print(f"FAIL {t}/{case}: " + "; ".join(problems))
            elif a.verbose:
                print(f"ok   {t}/{case}")
        print(f"{len(cases) - fails}/{len(cases)} pass")
        sys.exit(1 if fails else 0)
    finally:
        shutil.rmtree(site)


if __name__ == "__main__":
    main()
