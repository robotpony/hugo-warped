#!/usr/bin/env python3
"""Check the fences in Markdown files against hugo-warped's fence spec.

    tools/check-fences.py ~/writing/not-a-chef/content
    tools/check-fences.py docs/rules --every-block-is-a-fence --strict
    tools/check-fences.py content --keys formula=<fugu>/assets/icons/formula \\
        --keys stack=<fugu>/assets/icons/layers

Finds every fenced code block whose type is one of the spec's nine
(fences/README.md, "Fence types"), reads it as its type page says, and
prints one line per warning, in the hooks' form:

    WARN  table [too-many-cells]: "K | 0 | free" in "golf-4.md:31:1"

Ordinary code blocks (```bash) are never read. Page checks
(duplicate-name, duplicate-block, unclosed-fence) need the whole file,
so only this checker raises them, not a hook. Fences inside a `tabs`
panel are checked too, since the panel renders as Markdown.

Some checks depend on the target:

- unknown-token needs the target's icon or layer keys, so it runs only
  for a type given --keys TYPE=PATH (a folder of <key>.svg, or a JSON
  list).
- unknown-type runs only with --every-block-is-a-fence, for projects
  where every block is meant to be a fence (Scorekeep's rules pages).
- unknown-draw isn't checked: it needs the drawings a target knows.
- duplicate-name and duplicate-block skip a pair of blocks that both sit
  inside Scorekeep's `@if … @end`, since only one branch survives.

Warnings never fail a build, so it exits 0 unless --strict is given and
something warned. --json prints each block's parse, in the shape of
fences/fixtures/<type>/<case>.json. Stdlib only.
"""
import argparse
import json
import os
import re
import sys

KINDS = {
    "formula": "diagram", "stack": "diagram", "timeline": "diagram", "flow": "diagram",
    "table": "data", "reminders": "data",
    "diagram": "placeholder", "example": "placeholder", "sheet": "placeholder", "house-rules": "placeholder",
    "tabs": "layout",
}
ONE_PER_PAGE = {"reminders", "sheet", "house-rules"}

FENCE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
KEYWORD = re.compile(r"^([a-z][a-z-]*):(?:\s+(.*))?$")
TYPE = re.compile(r"^([a-z][a-z-]*)(?:\s+(.*))?$")
ATTR = re.compile(r'\s*([A-Za-z_][\w-]*)="([^"]*)"')


# Lines

def strip_note(line):
    """A line-read line with its note dropped and trimmed (README, "Notes")."""
    line = line.replace("\\←", "\x00l").replace("\\<-", "\x00a")
    line = re.sub(r"(?:^|\s+)(?:←|<-).*$", "", line)
    return line.replace("\x00l", "←").replace("\x00a", "<-").strip()


def keyword(line):
    m = KEYWORD.match(line)
    return (m.group(1), (m.group(2) or "").strip()) if m else None


def cells(line):
    return [c.strip() for c in line.split("|")]


def parse_attributes(raw):
    """The opening line's {…} group as a dict, or None when it doesn't parse."""
    raw = raw.strip()
    if not raw:
        return {}
    if not (raw.startswith("{") and raw.endswith("}")):
        return None
    inner, out, at = raw[1:-1], {}, 0
    while inner[at:].strip():
        m = ATTR.match(inner, at)
        if not m:
            return None
        out[m.group(1)] = m.group(2)
        at = m.end()
    return out


class Block:
    """One fence's parse, in the fixtures' shape."""

    def __init__(self, type_, attributes):
        self.type, self.attributes = type_, attributes
        self.lines, self.warnings, self.fallback = [], [], False
        self.extra = {}

    def warn(self, line, code, text=""):
        self.warnings.append({"line": line, "code": code, "text": text})

    def result(self):
        out = {"type": self.type, "kind": KINDS[self.type], "attributes": self.attributes}
        out.update(self.extra)
        out["lines"] = self.lines
        out["warnings"] = [{"line": w["line"], "code": w["code"]} for w in self.warnings]
        out["fallback"] = self.fallback
        return out


def read_lines(body):
    """(line number, line) for each line-read line, the opening fence as 1; blank and note-only lines left out."""
    for n, raw in enumerate(body, start=2):
        line = strip_note(raw)
        if line:
            yield n, line, raw


def no_valid_lines(b):
    b.warn(1, "no-valid-lines")
    b.fallback = True


# Types

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = "♠♥♦♣"


def table_token(t):
    """A column-1 token, None for a word, or "bad-run"."""
    if t in RANKS:
        return {"rank": t}
    if t == "Joker":
        return {"joker": True}
    if t in SUITS and len(t) == 1:
        return {"suit": t}
    if m := re.fullmatch(r"d([1-6])", t):
        return {"die": int(m.group(1))}
    if m := re.fullmatch(r"stack:(10|[2-9AJQK])([♠♥♦♣])", t):
        return {"stack": {"rank": m.group(1), "suit": m.group(2)}}
    if m := re.fullmatch(r"(.+?)-(.+)", t):
        a, b = table_token(m.group(1)), table_token(m.group(2))
        if a and b and a != "bad-run" and b != "bad-run":
            if "rank" in a and "rank" in b and RANKS.index(a["rank"]) < RANKS.index(b["rank"]):
                return {"run": [a["rank"], b["rank"]]}
            return "bad-run"
    return None


def parse_table(b, body, keys):
    seen, trailer, rows = set(), None, 0
    for n, line, _ in read_lines(body):
        if kw := keyword(line):
            key, value = kw
            if key not in ("head", "caption"):
                b.warn(n, "unknown-keyword", line)
            elif key in seen:
                b.warn(n, "duplicate-keyword", line)
            elif key == "head" and trailer == "caption":
                b.warn(n, "out-of-order", line)
            elif key == "head" and (len(cells(value)) != 2 or not all(cells(value))):
                b.warn(n, "bad-head", line)
            else:
                seen.add(key)
                trailer = key
                entry = {"line": n, "keyword": key, "value": value}
                if key == "head":
                    entry["cells"] = cells(value)
                b.lines.append(entry)
            continue
        if trailer:
            b.warn(n, "out-of-order", line)
            continue
        c = cells(line)
        if len(c) > 2:
            b.warn(n, "too-many-cells", line)
            continue
        if len(c) < 2 or not all(c):
            b.warn(n, "missing-cell", line)
            continue
        tokens = [table_token(t) for t in c[0].split()]
        if "bad-run" in tokens:
            b.warn(n, "bad-run", line)
            continue
        entry = {"line": n, "row": c, "marker": None}
        if all(tokens):
            entry["tokens"] = tokens
        else:
            entry["label"] = c[0]
            if any(tokens):
                b.warn(n, "mixed-token-cell", line)
        b.lines.append(entry)
        rows += 1
    if not rows:
        no_valid_lines(b)


def parse_reminders(b, body, keys):
    for n, line, _ in read_lines(body):
        if keyword(line):
            b.warn(n, "unknown-keyword", line)
        elif re.match(r"^(?:[-*+]|\d+[.)])\s", line):
            b.warn(n, "list-marker", line)
        else:
            b.lines.append({"line": n, "text": line})
    if not b.lines:
        no_valid_lines(b)


def parse_formula(b, body, keys):
    known = keys.get("formula")
    seen, trailer, after_result, operator, slots = set(), False, False, None, []
    for n, line, _ in read_lines(body):
        if kw := keyword(line):
            key, value = kw
            if key not in ("caption", "bar"):
                b.warn(n, "unknown-keyword", line)
            elif key in seen:
                b.warn(n, "duplicate-keyword", line)
            else:
                seen.add(key)
                trailer = True
                b.lines.append({"line": n, "keyword": key, "value": value})
            continue
        if trailer or after_result:
            b.warn(n, "out-of-order", line)
            continue
        marker, rest = None, line
        if m := re.match(r"^(\+|:|→|->|=)\s+(.*)$", line):
            marker, rest = ("→" if m.group(1) == "->" else m.group(1)), m.group(2)
        c = cells(rest)
        if len(c) > 4:
            b.warn(n, "too-many-cells", line)
            c = c[:4]
        if len(c) < 2 or not c[0] or not c[1]:
            b.warn(n, "missing-cell", line)
            continue
        if marker and not slots:
            b.warn(n, "stray-marker", line)
            marker = None
        elif marker and marker != "=":
            if operator and marker != operator:
                b.warn(n, "mixed-markers", line)
            else:
                operator = marker
        after_result = marker == "="
        icons = c[0].split()
        swaps = [s.strip() for s in c[3].split(",") if s.strip()] if len(c) > 3 else []
        if len(icons) > 2 or len(swaps) > 3:
            b.warn(n, "over-limit", line)
        if known is not None and any(i not in known for i in icons):
            b.warn(n, "unknown-token", line)
        entry = {"line": n, "row": c, "marker": marker, "icons": icons, "swaps": swaps}
        b.lines.append(entry)
        slots.append(entry)
    if len(slots) > 5:
        b.warn(slots[5]["line"], "over-limit")
    if not slots:
        no_valid_lines(b)


def parse_stack(b, body, keys):
    known = keys.get("stack")
    seen, trailer, layers, repeats = set(), False, 0, []
    for n, line, _ in read_lines(body):
        if kw := keyword(line):
            key, value = kw
            if key == "caption":
                if "caption" in seen:
                    b.warn(n, "duplicate-keyword", line)
                    continue
                seen.add(key)
                trailer = True
                b.lines.append({"line": n, "keyword": key, "value": value})
            elif key == "repeat":
                trailer = True
                m = re.fullmatch(r"(\d+)(?:\s*-\s*(\d+))?\s*[x×]\s*(\S+)", value)
                if not m or not m.group(3).isdigit() or int(m.group(3)) < 2:
                    b.warn(n, "bad-repeat", line)
                    continue
                a = int(m.group(1))
                z = int(m.group(2)) if m.group(2) else a
                if z < a:
                    b.warn(n, "bad-repeat", line)
                    continue
                entry = {"line": n, "keyword": key, "value": value, "from": a, "to": z, "times": int(m.group(3))}
                b.lines.append(entry)
                repeats.append(entry)
            else:
                b.warn(n, "unknown-keyword", line)
            continue
        if trailer:
            b.warn(n, "out-of-order", line)
            continue
        c = cells(line)
        if len(c) > 3:
            b.warn(n, "too-many-cells", line)
            c = c[:3]
        if len(c) < 2 or not c[0] or not c[1]:
            b.warn(n, "missing-cell", line)
            continue
        layer = re.sub(r"\s*\+\s*", "+", c[0])
        if known is not None and layer not in known:
            b.warn(n, "unknown-token", line)
        b.lines.append({"line": n, "row": c, "marker": None, "layer": layer})
        layers += 1
    for r in repeats:
        if r["from"] < 1 or r["to"] > layers:
            b.warn(r["line"], "bad-repeat")
            b.lines.remove(r)
    if not layers:
        no_valid_lines(b)


def parse_timeline(b, body, keys):
    for n, line, _ in read_lines(body):
        if keyword(line):
            b.warn(n, "unknown-keyword", line)
        elif m := re.fullmatch(r"(~?)(\d{4})\s+(.+)", line):
            b.lines.append({"line": n, "marker": m.group(1) or None, "year": int(m.group(2)), "label": m.group(3)})
        elif re.fullmatch(r"~?\d{4}", line):
            b.warn(n, "missing-label", line)
        else:
            b.warn(n, "bad-year", line)
    if not b.lines:
        no_valid_lines(b)


def parse_flow(b, body, keys):
    lines = list(read_lines(body))
    row_mode = any((kw := keyword(line)) and kw[0] == "row" for _, line, _ in lines)
    caption, rows, current = False, [], None
    if not row_mode:
        current = {"head": None, "steps": []}
        rows.append(current)
    for n, line, _ in lines:
        kw = keyword(line)
        if kw and kw[0] == "caption":
            if caption:
                b.warn(n, "duplicate-keyword", line)
            else:
                caption = True
                b.lines.append({"line": n, "keyword": "caption", "value": kw[1]})
            continue
        if caption:
            b.warn(n, "out-of-order", line)
            continue
        if kw and kw[0] == "row":
            current = {"head": {"line": n, "keyword": "row", "value": kw[1]}, "steps": []}
            rows.append(current)
            b.lines.append(current)  # replaced by its lines below
            continue
        if kw:
            b.warn(n, "unknown-keyword", line)
            continue
        if current is None:
            b.warn(n, "out-of-order", line)
            continue
        marker, rest = None, line
        if m := re.match(r"^(?:→|->)\s+(.*)$", line):
            marker, rest = "→", m.group(1)
        c = cells(rest)
        if len(c) > 2:
            b.warn(n, "too-many-cells", line)
            continue
        if not c[0]:
            b.warn(n, "missing-cell", line)
            continue
        if marker and not current["steps"]:
            b.warn(n, "stray-marker", line)
            marker = None
        step = {"line": n, "row": c, "marker": marker}
        current["steps"].append(step)
        if not row_mode:
            b.lines.append(step)
    drawn = [r for r in rows if r["steps"]]
    if row_mode:
        flat = []
        for entry in b.lines:
            if "steps" not in entry:
                flat.append(entry)
            elif entry["steps"]:
                flat += [entry["head"]] + entry["steps"]
            else:
                b.warn(entry["head"]["line"], "empty-group")
        b.lines = flat
        if len(drawn) > 3:
            b.warn(drawn[3]["head"]["line"], "over-limit")
    for r in drawn:
        if len(r["steps"]) > 5:
            b.warn(r["steps"][5]["line"], "over-limit")
    if not drawn:
        no_valid_lines(b)


def parse_placeholder(b, body, keys):
    for n, line, _ in read_lines(body):
        if b.lines:
            b.warn(n, "extra-line", line)
        else:
            b.lines.append({"line": n, "text": line})
    if not b.lines:
        b.warn(1, "empty-placeholder")
    words = b.attributes.get("draw", "").split()
    if b.type == "diagram":
        draw = words or ["table"]
    elif b.type == "example":
        draw = words[:1]
        if not words:
            b.warn(1, "missing-draw")
        elif len(words) > 1:
            b.warn(1, "too-many-draw")
    else:
        draw = None
        if "draw" in b.attributes:
            b.warn(1, "ignored-draw")
    b.extra = {"draw": draw, "description": b.lines[0]["text"] if b.lines else None}


def parse_tabs(b, body, keys):
    layout = b.attributes.get("layout")
    if layout is not None and layout not in ("side", "stack"):
        b.warn(1, "unknown-layout")
    panels, panel, inner = [], None, None
    for n, raw in enumerate(body, start=2):
        if inner:
            if (m := FENCE.match(raw)) and m.group(2)[0] == inner[0] and len(m.group(2)) >= len(inner) \
                    and not m.group(3).strip():
                inner = None
        else:
            line = strip_note(raw)
            if m := re.fullmatch(r"tab:(?:\s+(.*))?", line):
                panel = {"line": n, "keyword": "tab", "value": (m.group(1) or "").strip(), "body": []}
                panels.append(panel)
                continue
            if m := FENCE.match(raw):
                inner = m.group(2)
        if panel:
            panel["body"].append(raw)
        elif raw.strip():
            b.warn(n, "out-of-order", raw.strip())
    for p in panels:
        lines = p["body"]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        p["body"] = "\n".join(lines)
        if not p["value"]:
            b.warn(p["line"], "missing-label")
            p["value"] = "Tab"
        if not p["body"].strip():
            b.warn(p["line"], "empty-group")
    if len(panels) > 6:
        b.warn(panels[6]["line"], "over-limit")
    b.lines = panels
    if not panels:
        no_valid_lines(b)


PARSERS = {
    "table": parse_table, "reminders": parse_reminders, "formula": parse_formula, "stack": parse_stack,
    "timeline": parse_timeline, "flow": parse_flow, "tabs": parse_tabs,
    "diagram": parse_placeholder, "example": parse_placeholder, "sheet": parse_placeholder,
    "house-rules": parse_placeholder,
}


def parse_block(type_, rest, body, keys=None):
    """One fence: its type, the opening line after the type, and its body lines."""
    attributes = parse_attributes(rest)
    bad = attributes is None
    b = Block(type_, attributes or {})
    if bad:
        b.warn(1, "bad-attributes", rest.strip())
    PARSERS[type_](b, body, keys or {})
    return b


# Pages

def find_fences(lines, offset=0):
    """(opening line, info, body, closed) for each top-level fence, numbered from 1 + offset."""
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m or (m.group(2)[0] == "`" and "`" in m.group(3)):
            i += 1
            continue
        run, start, body = m.group(2), i, []
        i += 1
        closed = False
        while i < len(lines):
            c = FENCE.match(lines[i])
            if c and c.group(2)[0] == run[0] and len(c.group(2)) >= len(run) and not c.group(3).strip():
                closed = True
                break
            body.append(lines[i])
            i += 1
        yield start + 1 + offset, m.group(3).strip(), body, closed
        i += 1


def if_regions(lines):
    """The line numbers inside Scorekeep's @if … @end."""
    inside, depth = set(), 0
    for n, line in enumerate(lines, start=1):
        if re.match(r"^@if\b", line.strip()):
            depth += 1
        elif line.strip() == "@end" and depth:
            depth -= 1
        elif depth:
            inside.add(n)
    return inside


def check_page(text, keys=None, every_block_is_a_fence=False):
    """Every fence in a page: a list of (opening line, Block or None, page warnings)."""
    lines = text.replace("\r\n", "\n").split("\n")
    conditional = if_regions(lines)
    found, page = [], []

    def scan(region, offset):
        for at, info, body, closed in find_fences(region, offset):
            m = TYPE.match(info)
            if not m or m.group(1) not in KINDS:
                if every_block_is_a_fence and info:
                    page.append({"line": at, "code": "unknown-type", "type": info.split(" ")[0]})
                continue
            if not closed:
                page.append({"line": at, "code": "unclosed-fence", "type": m.group(1)})
            b = parse_block(m.group(1), m.group(2) or "", body, keys)
            found.append((at, b))
            if b.type == "tabs":
                scan(body, at)

    scan(lines, 0)
    names, once = {}, {}
    for at, b in found:
        for seen, key, code in ((names, b.attributes.get("name"), "duplicate-name"),
                                (once, b.type if b.type in ONE_PER_PAGE else None, "duplicate-block")):
            if key is None:
                continue
            if key in seen and not (seen[key] in conditional and at in conditional):
                page.append({"line": at, "code": code, "type": b.type})
            seen.setdefault(key, at)
    return found, page


def page_warnings(found, page):
    """Every warning on a page, at its file line: (line, type, code, text)."""
    out = [(w["line"], w["type"], w["code"], "") for w in page]
    for at, b in found:
        out += [(at + w["line"] - 1, b.type, w["code"], w["text"]) for w in b.warnings]
    return sorted(out)


# Command line

def load_keys(specs):
    keys = {}
    for spec in specs or []:
        type_, _, path = spec.partition("=")
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            keys[type_] = {f[:-4] for f in os.listdir(path) if f.endswith(".svg")}
        else:
            with open(path) as f:
                keys[type_] = set(json.load(f))
    return keys


def markdown_files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d != "node_modules")
                yield from (os.path.join(root, f) for f in sorted(files) if f.endswith(".md"))
        else:
            yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="+", help="Markdown files or folders")
    ap.add_argument("--keys", action="append", metavar="TYPE=PATH",
                    help="the target's keys for formula or stack: a folder of <key>.svg, or a JSON list")
    ap.add_argument("--every-block-is-a-fence", action="store_true",
                    help="warn unknown-type on a code block that isn't a fence type")
    ap.add_argument("--strict", action="store_true", help="exit 1 when anything warns")
    ap.add_argument("--json", action="store_true", help="print each block's parse instead of warnings")
    a = ap.parse_args()
    keys = load_keys(a.keys)
    count, parses = 0, []
    for path in markdown_files(a.paths):
        with open(path, encoding="utf-8") as f:
            found, page = check_page(f.read(), keys, a.every_block_is_a_fence)
        if a.json:
            parses += [dict(b.result(), file=path, at=at) for at, b in found]
            parses += [dict(w, file=path) for w in page]
            continue
        for line, type_, code, text in page_warnings(found, page):
            quoted = f" {json.dumps(text, ensure_ascii=False)}" if text else ""
            print(f'WARN  {type_} [{code}]:{quoted} in "{path}:{line}:1"')
            count += 1
    if a.json:
        print(json.dumps(parses, ensure_ascii=False, indent=1))
    sys.exit(1 if a.strict and (count or any("code" in p for p in parses)) else 0)


if __name__ == "__main__":
    main()
