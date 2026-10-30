#!/usr/bin/env python3
"""Suggest and mark glossary terms, as hugo-warped's glossary spec says.

    tools/glossary.py candidates ~/writing/not-a-chef/content --glossary reference/glossary
    tools/glossary.py link ~/writing/not-a-chef/content --glossary reference/glossary \\
        --skip ~/writing/not-a-chef/tools/glossary-skip.txt [--term Fond] [--check [--strict] | --apply answers.json]

candidates prints words on two or more pages that aren't yet a term or
an `also` form, and are rare in everyday English (not in
tools/data/common-en.txt) or set in italics. link finds each term's
first prose mention on every page without a mark for it, shows it as a
diff and asks: yes, never on this page (saved to the skip file), skip
for now, all of the term's remaining ones (after typing their count),
or quit. --check lists those mentions and writes nothing; --apply takes
the answers from a JSON file instead of asking.

An entry with no body is a stub: it isn't linked, but its words are
known, so they aren't suggested either. Entry problems (missing-title,
aliases-not-also, empty-definition, duplicate-key) print as warnings on stderr and never stop a run.
--json prints a run's results as data. Stdlib only.
"""
import argparse
import json
import os
import re
import shutil
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(HERE, "data", "common-en.txt")

FENCE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:\s+(.*?))?\s*#*\s*$")
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1")
WIKI = re.compile(r"\[\[([^\]|\\]+?)(?:\\?\|([^\]]+))?\]\]")
MD_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
HTML_A = re.compile(r"<a\b[^>]*>.*?</a>", re.I)
HTML_TAG = re.compile(r"</?[A-Za-z][^>]*>")
URL = re.compile(r"<?https?://[^\s>)]+>?")
ITALIC = re.compile(r"(?<![*_\w])([*_])(?![*_\s])(.+?)(?<![*_\s])\1(?![*_\w])")
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")
SUFFIXES = ("ification", "ifying", "ifiers", "ifier", "ifies", "ified", "ify", "ations", "ation",
            "ings", "ing", "ions", "ion", "ers", "er", "ies", "ied", "ed", "es", "s", "y", "e")


def nfc(s):
    return unicodedata.normalize("NFC", s)


def match_key(s):
    """Lowercase, runs of non-letters/digits as one space, trimmed."""
    return re.sub(r"[\W_]+", " ", nfc(s).lower()).strip()


def anchor(s):
    return re.sub(r"[\W_]+", "-", nfc(s).lower()).strip("-")


def letter(key):
    c = key[:1].upper()
    return c if c.isalpha() else "#"


# Front matter (the YAML a glossary needs: scalars and lists)

def scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def front_matter(text):
    """(fields, body, body's first line number). Lists are flow or block."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text, 1
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            break
    else:
        return {}, text, 1
    fields, last = {}, None
    for raw in lines[1:end]:
        if m := re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw):
            last, v = m.group(1), m.group(2).strip()
            if v.startswith("[") and v.endswith("]"):
                fields[last] = [scalar(x) for x in v[1:-1].split(",") if x.strip()]
            else:
                fields[last] = scalar(v) if v else None
        elif (m := re.match(r"^\s+-\s+(.*)$", raw)) and last:
            if not isinstance(fields.get(last), list):
                fields[last] = []
            fields[last].append(scalar(m.group(1)))
        elif raw.strip() and not raw.startswith((" ", "\t")):
            last = None
    return fields, "\n".join(lines[end + 1:]), end + 2


# Reading a page

def read_lines(body, first):
    """(line number, line, kind) for a page body: kind is "prose",
    "heading" or "code". A tabs fence's panels are prose, and a fence
    closes at a line of its character, at least as long, with nothing
    after it."""
    stack = []  # (fence, is_tabs)
    for n, line in enumerate(body.split("\n"), start=first):
        m = FENCE.match(line)
        if stack and not stack[-1][1]:
            if m and m.group(2)[0] == stack[-1][0][0] and len(m.group(2)) >= len(stack[-1][0]) \
                    and not m.group(3).strip():
                stack.pop()
            yield n, line, "code"
            continue
        if m:
            if stack and m.group(2)[0] == stack[-1][0][0] and len(m.group(2)) >= len(stack[-1][0]) \
                    and not m.group(3).strip():
                stack.pop()
                yield n, line, "code"
                continue
            info = m.group(3).strip().split()
            stack.append((m.group(2), bool(info) and info[0] == "tabs"))
            yield n, line, "code"
            continue
        yield n, line, "heading" if HEADING.match(line) else "prose"


def blank(line, pattern, keep=None):
    """The line with each match turned to NULs (same length), or to its
    group `keep` padded with NULs, so positions still line up."""
    def sub(m):
        if keep is None:
            return "\0" * len(m.group(0))
        start = m.start(keep) - m.start(0)
        text = m.group(keep)
        return "\0" * start + text + "\0" * (len(m.group(0)) - start - len(text))
    return pattern.sub(sub, line)


def mark_spans(body, first):
    """[(line, start, end, target, text)] for every mark in prose."""
    out = []
    for n, line, kind in read_lines(body, first):
        if kind == "code":
            continue
        for m in WIKI.finditer(blank(nfc(line), CODE_SPAN)):
            out.append((n, m.start(), m.end(), m.group(1).strip(), (m.group(2) or m.group(1)).strip()))
    return out


def marks(body, first):
    """[(line, target, text)] for every mark in prose."""
    return [(n, t, x) for n, _, _, t, x in mark_spans(body, first)]


class Page:
    def __init__(self, root, path):
        self.path = os.path.relpath(path, root).replace(os.sep, "/")
        self.file = path
        with open(path, encoding="utf-8") as f:
            self.text = f.read()
        self.fields, self.body, self.first = front_matter(self.text)

    def marks(self):
        return marks(self.body, self.first)


def pages(root, glossary=None, inside=False):
    """Every content page, by path; only the glossary's, or only the rest."""
    out = []
    for d, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            if name.endswith(".md"):
                p = Page(root, os.path.join(d, name))
                if glossary is None or p.path.startswith(glossary + "/") == inside:
                    out.append(p)
    return sorted(out, key=lambda p: p.path)


# The glossary

def warn(code, path, detail=""):
    print(f"WARN  glossary [{code}]: {detail + ' ' if detail else ''}in \"{path}\"", file=sys.stderr)


def load(root, folder, stubs=False, quiet=()):
    """(entries sorted by key, warnings). Each entry is a dict of term,
    also, key, keys, anchor, letter and path. A stub (an entry with no
    body) holds its keys but is left out, unless `stubs`. Warnings with a
    code in `quiet` are returned but not printed."""
    folder = folder.strip("/")
    entries, seen, warnings = [], {}, []

    def w(code, path, detail=""):
        warnings.append({"path": path, "code": code})
        if code not in quiet:
            warn(code, path, detail)

    for p in pages(root, folder, inside=True):
        if os.path.basename(p.path) == "_index.md":
            continue
        term = p.fields.get("title")
        if not term:
            w("missing-title", p.path)
            continue
        if "aliases" in p.fields:
            w("aliases-not-also", p.path)
        stub = not p.body.strip()
        if stub:
            w("empty-definition", p.path, "a stub, left out until it's written,")
        also = p.fields.get("also") or []
        if isinstance(also, str):
            also = [also]
        keys = []
        for form in [term] + also:
            k = match_key(form)
            if not k or k in keys:
                continue
            if k in seen:
                w("duplicate-key", p.path, f'"{form}" is already {seen[k]}\'s')
                continue
            seen[k] = term
            keys.append(k)
        if stub and not stubs:
            continue
        entries.append({"term": term, "also": also, "kind": p.fields.get("kind") or "",
                        "key": match_key(term), "keys": keys,
                        "anchor": anchor(term), "letter": letter(match_key(term)),
                        "path": p.path, "forms": [f for f in [term] + also if match_key(f) in keys]})
    entries.sort(key=lambda e: e["key"])
    return entries, warnings


def resolve(entries, target):
    k = match_key(target)
    return next((e for e in entries if k in e["keys"]), None)


# link

LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
HEADING_ATTRS = re.compile(r"\s*\{([^}]*)\}\s*$")


def skipped(page, lines, rules):
    """Line numbers never read: each section headed by one of
    rules["sections"], down to the next heading at its level or above;
    and on a recipe page (under one of rules["recipes"]), the list items
    under any h2 none of whose words is in rules["not_ingredients"], or
    marked {.article}, down to the next h2."""
    recipe = any(page.path.startswith(r.strip("/") + "/") for r in rules["recipes"])
    out, level, ingredients, in_item = set(), None, False, False
    for n, line, kind in lines:
        if kind == "heading":
            m = HEADING.match(line)
            depth, title = len(m.group(1)), (m.group(2) or "").strip()
            attrs = HEADING_ATTRS.search(title)
            title = HEADING_ATTRS.sub("", title)
            if level is not None and depth <= level:
                level = None
            if depth <= 2:
                article = bool(attrs) and ".article" in attrs.group(1).split()
                ingredients = recipe and depth == 2 and not article \
                    and not set(match_key(title).split()) & rules["not_ingredients"]
            in_item = False
            if level is None and title.lower() in rules["sections"]:
                level = depth
                continue
        if level is not None:
            out.add(n)
        elif ingredients and kind == "prose":
            # A list item runs on to the next blank line.
            if LIST_ITEM.match(line):
                in_item = True
            elif not line.strip():
                in_item = False
            if in_item:
                out.add(n)
    return out


def late(page, lines, rules):
    """Line numbers on a recipe page under an h2 named in
    rules["sidebar"] (the whole title, any case, a trailing colon
    dropped), down to the next h2: read after the rest of the page."""
    if not rules["sidebar"] or not any(page.path.startswith(r.strip("/") + "/") for r in rules["recipes"]):
        return set()
    out, inside = set(), False
    for n, line, kind in lines:
        if kind == "heading" and len(HEADING.match(line).group(1)) <= 2:
            title = HEADING_ATTRS.sub("", (HEADING.match(line).group(2) or "")).strip().rstrip(":").strip()
            inside = len(HEADING.match(line).group(1)) == 2 and title.lower() in rules["sidebar"]
        elif inside:
            out.add(n)
    return out


def masked(line):
    for pat in (CODE_SPAN, WIKI, MD_LINK, HTML_A, URL, HTML_TAG):
        line = blank(line, pat)
    return line


def first_mention(page, entry, rules, body=None):
    """(line, start, end) of the entry's first mention in prose, reading
    a recipe's sidebar sections last; ingredient lists count only for an
    entry of kind "ingredient". `body` stands in for the page's own."""
    forms = sorted(entry["forms"], key=len, reverse=True)
    pat = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(nfc(f)) for f in forms) + r")(?!\w)", re.I)
    lines = list(read_lines(page.body if body is None else body, page.first))
    skip = set() if entry.get("kind") == "ingredient" else skipped(page, lines, rules)
    after = late(page, lines, rules)
    longer = [(f, r) for t, f, r in rules.get("claims", ()) if t != entry["term"]]
    for wanted_late in (False, True):
        for n, line, kind in lines:
            if kind != "prose" or n in skip or (n in after) != wanted_late:
                continue
            text = masked(nfc(line))
            for m in pat.finditer(text):
                if not claimed(text, m, longer):
                    return n, m.start(), m.end()
    return None


def claimed(text, m, longer):
    """Whether another entry's longer form covers match m: those words
    are that entry's, not this one's ("garam masala" in "garam masala
    water")."""
    size = m.end() - m.start()
    for form, regex in longer:
        if len(form) > size:
            for c in regex.finditer(text):
                if c.start() <= m.start() and c.end() >= m.end():
                    return True
    return False


def claims(root, folder):
    """(term, form, regex) for every form of every entry, stubs too."""
    entries, _ = load(root, folder, stubs=True, quiet={"missing-title", "aliases-not-also", "empty-definition",
                                                        "duplicate-key"})
    return [(e["term"], nfc(f), re.compile(r"(?<!\w)" + re.escape(nfc(f)) + r"(?!\w)", re.I))
            for e in entries for f in e["forms"]]


def read_skip(path):
    out = set()
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if " | " in line:
                    page, term = line.split(" | ", 1)
                    out.add((page.strip(), term.strip()))
    return out


def hit(root, folder, p, e, entries, skip, rules):
    """Where entry e's mark belongs on page p, if it isn't there yet:
    (line, start, end, moved). `moved` is None for a new mark, or
    (line, start, end, words) for the page's one existing mark, which
    the new one replaces; start and end are then on the line with that
    mark back to plain words. None when there's nothing to do."""
    if p.path == e["path"] or os.path.basename(p.path) == "_index.md" and p.path.startswith(folder + "/"):
        return None
    if (p.path, e["term"]) in skip:
        return None
    spans = [m for m in mark_spans(p.body, p.first) if resolve(entries, m[3]) is e]
    if not spans:
        h = first_mention(p, e, rules)
        return h + (None,) if h else None
    if len(spans) > 1:
        return None
    n, ms, me, _, words = spans[0]
    lines = unmarked(p, (n, ms, me, words))
    h = first_mention(p, e, rules, body="\n".join(lines[p.first - 1:]))
    if not h or (h[0], h[1]) == (n, ms):
        return None
    return h + ((n, ms, me, words),)


def unmarked(p, moved):
    """The page's lines, with a mark at `moved` back to plain words."""
    lines = nfc(p.text).split("\n")
    if moved:
        n, ms, me, words = moved
        lines[n - 1] = lines[n - 1][:ms] + words + lines[n - 1][me:]
    return lines


def proposals(root, folder, skip, rules, entries=None):
    """Yield (entry, [(page, line, start, end, moved), …]) for every entry
    with a mark to add or move, A to Z. Each entry's list is read when it's
    reached, so it sees the edits made for the entries before it."""
    if entries is None:
        entries, _ = load(root, folder)
    for e in entries:
        found = [(p,) + h for p in pages(root) if (h := hit(root, folder, p, e, entries, skip, rules))]
        if found:
            yield e, found


def only_terms(entries, terms):
    """The entries named by `terms` (a title or also form, any case), or all."""
    if not terms:
        return entries
    keys = {match_key(t) for t in terms}
    return [e for e in entries if keys & set(e["keys"])]


def write_mark(p, e, n, s, end, moved=None):
    lines = unmarked(p, moved)
    old = lines[n - 1]
    lines[n - 1] = old[:s] + mark_for(e, old[s:end]) + old[end:]
    p.text = "\n".join(lines)
    with open(p.file, "w", encoding="utf-8") as f:
        f.write(p.text)


def write_never(skip_file, skip, p, e):
    if skip_file and (p.path, e["term"]) not in skip:
        with open(skip_file, "a", encoding="utf-8") as f:
            f.write(f"{p.path} | {e['term']}\n")
    skip.add((p.path, e["term"]))


def skip_rules(a):
    return {"sections": {x.lower() for x in a.skip_section}, "recipes": a.recipes or [],
            "sidebar": {t.strip().rstrip(":").strip().lower() for x in getattr(a, "sidebar_headings", None) or [] for t in x.split(",")
                        if t.strip()},
            "not_ingredients": {w for x in a.not_ingredients or [] for w in match_key(x.replace(",", " ")).split()}}


def mark_for(entry, words):
    return f"[[{entry['term']}]]" if words == entry["term"] else f"[[{entry['term']}|{words}]]"


class Style:
    """ANSI styles for the link prompt, or none for NO_COLOR or a pipe."""

    def __init__(self, on):
        self.on = on

    def __call__(self, text, *codes):
        return f"\x1b[{';'.join(codes)}m{text}\x1b[0m" if self.on and text else text

    def dim(self, text):
        return self(text, "2")

    def bold(self, text):
        return self(text, "1")

    def mark(self, mark):
        """Bold green, with its brackets a dimmer green."""
        return self(mark[:2], "2", "32") + self(mark[2:-2], "1", "32") + self(mark[-2:], "2", "32")


def in_context(line, start, end, mark, width, style=None):
    """The line with line[start:end] replaced by `mark`, trimmed at word
    boundaries to fit `width`, with about as many words each side and an
    ellipsis where it's cut. With a Style, the mark is green and the rest
    dim."""
    left, right = line[:start], line[end:]
    room = max(width - len(mark), 2)
    if len(left) + len(right) > room:
        lb = min(len(left), max(room // 2, room - len(right)))
        rb = min(len(right), room - lb)
        if lb < len(left):
            cut = left[len(left) - lb + 1:] if lb > 1 else ""
            left = "…" + (cut.split(" ", 1)[1] if " " in cut[:-1] else cut)
        if rb < len(right):
            cut = right[:rb - 1] if rb > 1 else ""
            right = (cut.rsplit(" ", 1)[0] if " " in cut[1:] else cut) + "…"
    if not style:
        return left + mark + right
    return style.dim(left) + style.mark(mark) + style.dim(right)


def tally(c):
    moved = f", {c['moved']} moved" if c.get("moved") else ""
    return f"{c['linked']} linked{moved}, {c['never']} never, {c['skipped']} skipped"


def context_line(p, e, n, s, end, moved, width, st):
    old = unmarked(p, moved)[n - 1]
    indent = len(old) - len(old.lstrip())
    return in_context(old.strip(), s - indent, end - indent, mark_for(e, old[s:end]), width, st)


def was_line(p, moved, width, st):
    """Where a moved mark is now, dim."""
    n, ms, me, _ = moved
    old = nfc(p.text).split("\n")[n - 1]
    indent = len(old) - len(old.lstrip())
    return st.dim(f"{n}: ") + st.dim(in_context(old.strip(), ms - indent, me - indent, old[ms:me], width - len(f"{n}: ")))


def ask(prompt):
    try:
        ans = input(prompt)
    except EOFError:
        print()
        return None
    if not sys.stdin.isatty():
        print()
    return ans.strip()


def run_check(a, root, folder, skip, rules, entries):
    found = []
    for e, hits in proposals(root, folder, skip, rules, entries):
        for p, n, s, end, moved in hits:
            words = unmarked(p, moved)[n - 1][s:end]
            found.append({"path": p.path, "line": n, "term": e["term"], "words": words,
                          "move": bool(moved), "from": moved[0] if moved else None})
    if a.json:
        print(json.dumps(found, ensure_ascii=False, indent=2))
    else:
        for f in found:
            move = f'  (move from line {f["from"]})' if f["move"] else ""
            print(f'{f["path"]}:{f["line"]}  {f["term"]}  "{f["words"]}"{move}')
    return 1 if a.strict and found else 0


def run_apply(a, root, folder, skip, rules, entries):
    """Answers from a JSON list of {path, line, term, answer, from}, written
    as the interactive run would, skipping any whose mention has moved."""
    with open(a.apply, encoding="utf-8") as f:
        items = json.load(f)
    counts = {"linked": 0, "moved": 0, "never": 0, "skipped": 0, "stale": 0}
    for item in items:
        e = resolve(entries, item["term"])
        path = os.path.join(root, item["path"])
        answer = str(item.get("answer", "")).lower()
        h = None
        if e and os.path.exists(path):
            p = Page(root, path)
            h = hit(root, folder, p, e, entries, skip, rules)
        moved = h[3] if h else None
        ok = h and h[0] == item["line"] and (
            answer in ("never", "keep", "skip")
            or answer == "yes" and not moved
            or answer == "move" and moved and moved[0] == item.get("from"))
        if not ok:
            counts["stale"] += 1
            print(f'{item["path"]}:{item["line"]}  {item["term"]}  stale, not changed')
            continue
        if answer in ("yes", "move"):
            write_mark(p, e, *h)
            done = "moved" if moved else "linked"
        elif answer in ("never", "keep"):
            write_never(a.skip, skip, p, e)
            done = "never"
        else:
            done = "skipped"
        counts[done] += 1
        print(f'{p.path}:{h[0]}  {e["term"]}  {done}' + (f" from line {moved[0]}" if done == "moved" else ""))
    print(f"\nTotal: {tally(counts)}, {counts['stale']} stale. Review: git diff")
    return 0


def run_link(a):
    root, folder = a.content, a.glossary.strip("/")
    skip = read_skip(a.skip)
    rules = skip_rules(a)
    rules["claims"] = claims(root, folder)
    quiet = set() if a.check or a.apply else {"empty-definition"}
    all_entries, warnings = load(root, folder, quiet=quiet)
    entries = only_terms(all_entries, a.term)
    if a.check:
        return run_check(a, root, folder, skip, rules, entries)
    if a.apply:
        return run_apply(a, root, folder, skip, rules, all_entries)

    tty = sys.stdout.isatty() and sys.stdin.isatty()
    st = Style(sys.stdout.isatty() and "NO_COLOR" not in os.environ)
    width = shutil.get_terminal_size().columns
    stubs = sum(w["code"] == "empty-definition" for w in warnings)
    if stubs:
        print(st.dim(f"{stubs} stub{'s' if stubs != 1 else ''} skipped (not written yet)") + "\n")

    def prompt(moved):
        keys = (("y", "move here"), ("n", "keep where it is")) if moved else (("y", "yes"), ("n", "never here"))
        keys += (("s", "skip"), ("a", "all"), ("q", "quit"))
        return "  " + "  ".join(f"{st.bold(k)} {word}" for k, word in keys) + " › "

    def echo(text, code, extra=""):
        if tty:
            print("\x1b[1A\x1b[2K", end="")  # the prompt line gives way to its answer
        print("  " + st(text, code) + extra)

    counts, quit_ = {}, False
    for k, (e, hits) in enumerate(proposals(root, folder, skip, rules, entries)):
        term = e["term"]
        counts[term] = c = {"linked": 0, "moved": 0, "never": 0, "skipped": 0}
        if k:
            print("\n")
        heading = f"{term} · {len(hits)} page{'s' if len(hits) != 1 else ''}"
        print(st.bold(heading))
        print(st.dim("─" * min(max(len(heading), 20), width)) + "\n")
        i = 0
        while i < len(hits):
            p, n, s, end, moved = hits[i]
            if i:
                print("\n")
            print(f"  {st.dim(f'{i + 1}/{len(hits)}')}  {p.path}:{n}" + (st.dim(f"  move from {moved[0]}") if moved else "") + "\n")
            if moved:
                print("    " + was_line(p, moved, width - 4, st))
                print("    " + f"{n}: " + context_line(p, e, n, s, end, moved, width - 4 - len(f"{n}: "), st) + "\n")
            else:
                print("    " + context_line(p, e, n, s, end, moved, width - 4, st) + "\n")
            ans = ask(prompt(moved))
            ans = "q" if ans is None else ans.lower()[:1]
            if ans == "q":
                quit_ = True
                break
            if ans == "a":
                rest = [h for h in hits[i:] if (h[0].path, term) not in skip]
                print()
                for q, qn, qs, qend, qmoved in rest:
                    print("  " + st.dim(f"{q.path}:{qn}" + (f"  move from {qmoved[0]}" if qmoved else "")))
                    print("    " + context_line(q, e, qn, qs, qend, qmoved, width - 4, st))
                print()
                typed = ask(f"  Link all {len(rest)} remaining for {term}? "
                            f"Type {len(rest)} to confirm, or Enter to go back › ")
                if typed == str(len(rest)):
                    for h in rest:
                        write_mark(h[0], e, *h[1:])
                        c["moved" if h[4] else "linked"] += 1
                    echo(f"✓ linked {len(rest)} (all)", "32")
                    break
                print("\n")
                continue
            ans = ans if ans in ("y", "n") else "s"
            if ans == "y":
                write_mark(p, e, n, s, end, moved)
                c["moved" if moved else "linked"] += 1
                echo("✓ moved" if moved else "✓ linked", "32")
            elif ans == "n":
                write_never(a.skip, skip, p, e)
                c["never"] += 1
                echo("✗ kept" if moved else "✗ never", "33", st.dim(f"  saved to {a.skip}") if a.skip else "")
            else:
                c["skipped"] += 1
                echo("– skipped", "2")
            i += 1
        if quit_:
            break
    print("\n")
    total = {"linked": 0, "moved": 0, "never": 0, "skipped": 0}
    for t, c in counts.items():
        print(f"{t}: {tally(c)}")
        for key in total:
            total[key] += c[key]
    print(f"\nTotal: {tally(total)}. Review: git diff")
    return 0


# candidates

def stem(word):
    """A rough stem, so a word's forms group together: one suffix off,
    keeping at least four letters."""
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def prose_text(line):
    """A prose line as a reader sees it: link text kept, targets, URLs,
    code and tags dropped."""
    line = CODE_SPAN.sub(" ", line)
    line = WIKI.sub(lambda m: m.group(2) or m.group(1), line.replace("\\|", "|"))
    line = MD_LINK.sub(lambda m: m.group(1), line)
    line = URL.sub(" ", line)
    return HTML_TAG.sub(" ", line)


def run_candidates(a):
    root, folder = a.content, a.glossary.strip("/")
    entries, _ = load(root, folder, stubs=True)
    keys = {k for e in entries for k in e["keys"]}
    with open(a.common, encoding="utf-8") as f:
        common = {w.strip() for w in f if w.strip()}

    rules = skip_rules(a)
    word_pages, lower_seen, italic_pages, phrase_pages = {}, set(), {}, {}
    for p in pages(root, folder, inside=False):
        lines = list(read_lines(p.body, p.first))
        skip = skipped(p, lines, rules)
        for n, line, kind in lines:
            if kind == "code" or n in skip:
                continue
            text = nfc(prose_text(line)).replace("’", "'")
            for m in ITALIC.finditer(text):
                words = WORD.findall(m.group(2))
                phrase = " ".join(words).lower()
                if len(words) > 1:
                    phrase_pages.setdefault(phrase, set()).add(p.path)
                elif words and words[0] == phrase:
                    italic_pages.setdefault(phrase, set()).add(p.path)
            # A phrase's words count only as the phrase.
            text = ITALIC.sub(lambda m: m.group(0) if " " not in m.group(2).strip() else " ", text)
            for w in WORD.findall(text):
                lw = w.lower()
                if len(lw) < 3:
                    continue
                word_pages.setdefault(lw, set()).add(p.path)
                if w == lw:
                    lower_seen.add(lw)

    groups = {}
    for w, ps in word_pages.items():
        italic = len(italic_pages.get(w, ())) >= a.min_pages
        if match_key(w) in keys or not (w not in common or italic) or not (w in lower_seen or italic):
            continue
        groups.setdefault(stem(w), []).append((w, ps, italic))

    rows = []
    for forms in groups.values():
        forms.sort(key=lambda f: (-len(f[1]), f[0]))
        ps = set().union(*(f[1] for f in forms))
        if len(ps) < a.min_pages:
            continue
        rows.append({"word": forms[0][0], "pages": len(ps), "forms": [f[0] for f in forms[1:]],
                     "italics": all(f[0] in common for f in forms)})
    for phrase, ps in phrase_pages.items():
        if len(ps) >= a.min_pages and match_key(phrase) not in keys:
            rows.append({"word": phrase, "pages": len(ps), "forms": [], "italics": True})
    rows.sort(key=lambda r: (-r["pages"], r["word"]))

    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    print("  pages  word")
    for r in rows:
        extra = (f"  ({', '.join(r['forms'])})" if r["forms"] else "") + ("  (italics)" if r["italics"] else "")
        print(f"{r['pages']:>7}  {r['word']}{extra}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("candidates", "link"):
        s = sub.add_parser(name)
        s.add_argument("content", help="the site's content folder")
        s.add_argument("--glossary", required=True, help="the glossary folder, under content")
        s.add_argument("--json", action="store_true")
    for s in sub.choices.values():
        s.add_argument("--skip-section", action="append", default=None,
                       help='a heading whose section is never read (default "Ingredients")')
        s.add_argument("--recipes", action="append", metavar="FOLDER",
                       help="a folder under content whose pages are recipes, repeatable")
        s.add_argument("--not-ingredients", action="append", metavar="WORDS",
                       help="comma-separated words that keep a recipe's h2 from being an ingredient section")
        s.add_argument("--sidebar-headings", action="append", metavar="TITLES",
                       help="comma-separated h2 titles a recipe page reads last (its sidebar), repeatable")
    c = sub.choices["candidates"]
    c.add_argument("--min-pages", type=int, default=2)
    c.add_argument("--common", default=COMMON, help="common words, one per line")
    k = sub.choices["link"]
    k.add_argument("--skip", help="the skip file of never pairs")
    k.add_argument("--check", action="store_true", help="list unmarked first mentions; write nothing")
    k.add_argument("--strict", action="store_true", help="with --check, exit 1 when any are found")
    k.add_argument("--term", action="append", help="only this entry (its title or an also form), repeatable")
    k.add_argument("--apply", metavar="FILE",
                   help="answers as a JSON list of {path, line, term, answer: yes|never|skip}; asks nothing")
    a = ap.parse_args(argv)
    a.skip_section = a.skip_section or ["Ingredients"]
    if a.cmd == "link":
        return run_link(a)
    return run_candidates(a)


if __name__ == "__main__":
    sys.exit(main())
