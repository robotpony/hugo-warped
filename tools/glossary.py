#!/usr/bin/env python3
"""Suggest and mark glossary terms, as hugo-warped's glossary spec says.

    tools/glossary.py candidates ~/writing/not-a-chef/content --glossary reference/glossary
    tools/glossary.py link ~/writing/not-a-chef/content --glossary reference/glossary \\
        --skip ~/writing/not-a-chef/tools/glossary-skip.txt [--check [--strict]]

candidates prints words on two or more pages that aren't yet a term or
an `also` form, and are rare in everyday English (not in
tools/data/common-en.txt) or set in italics. link finds each term's
first prose mention on every page without a mark for it, shows it as a
diff and asks: yes, never on this page (saved to the skip file), skip
for now, or quit. --check lists those mentions and writes nothing.

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


def marks(body, first):
    """[(line, target, text)] for every mark in prose."""
    out = []
    for n, line, kind in read_lines(body, first):
        if kind == "code":
            continue
        for m in WIKI.finditer(blank(line, CODE_SPAN)):
            target = m.group(1).strip()
            out.append((n, target, (m.group(2) or m.group(1)).strip()))
    return out


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


def load(root, folder, stubs=False):
    """(entries sorted by key, warnings). Each entry is a dict of term,
    also, key, keys, anchor, letter and path. A stub (an entry with no
    body) holds its keys but is left out, unless `stubs`."""
    folder = folder.strip("/")
    entries, seen, warnings = [], {}, []

    def w(code, path, detail=""):
        warnings.append({"path": path, "code": code})
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
        entries.append({"term": term, "also": also, "key": match_key(term), "keys": keys,
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


def masked(line):
    for pat in (CODE_SPAN, WIKI, MD_LINK, HTML_A, URL, HTML_TAG):
        line = blank(line, pat)
    return line


def first_mention(page, entry, rules):
    forms = sorted(entry["forms"], key=len, reverse=True)
    pat = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(nfc(f)) for f in forms) + r")(?!\w)", re.I)
    lines = list(read_lines(page.body, page.first))
    skip = skipped(page, lines, rules)
    for n, line, kind in lines:
        if kind != "prose" or n in skip:
            continue
        if m := pat.search(masked(nfc(line))):
            return n, m.start(), m.end()
    return None


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


def proposals(root, folder, skip, rules):
    """Yield (entry, page, line, start, end) for every unmarked first
    mention, entry by entry, re-reading each page as it changes."""
    entries, _ = load(root, folder)
    for e in entries:
        for p in pages(root):
            if p.path == e["path"] or os.path.basename(p.path) == "_index.md" and p.path.startswith(folder + "/"):
                continue
            if (p.path, e["term"]) in skip:
                continue
            if any(resolve(entries, t) is e for _, t, _ in p.marks()):
                continue
            if hit := first_mention(p, e, rules):
                yield (e, p) + hit


def skip_rules(a):
    return {"sections": {x.lower() for x in a.skip_section}, "recipes": a.recipes or [],
            "not_ingredients": {w for x in a.not_ingredients or [] for w in match_key(x.replace(",", " ")).split()}}


def mark_for(entry, words):
    return f"[[{entry['term']}]]" if words == entry["term"] else f"[[{entry['term']}|{words}]]"


def in_context(line, start, end, mark, width, style=False):
    """The line with line[start:end] replaced by `mark`, trimmed at word
    boundaries to fit `width`, with about as many words each side and an
    ellipsis where it's cut. `style` makes the mark bold and the rest dim."""
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
    dim, bold, reset = "\x1b[2m", "\x1b[1m", "\x1b[0m"
    return f"{dim}{left}{reset}{bold}{mark}{reset}{dim}{right}{reset}"


def run_link(a):
    root, folder = a.content, a.glossary.strip("/")
    skip = read_skip(a.skip)
    rules = skip_rules(a)
    found = []
    if a.check:
        for e, p, n, s, end in proposals(root, folder, skip, rules):
            words = nfc(p.text.split("\n")[n - 1])[s:end]
            found.append({"path": p.path, "line": n, "term": e["term"], "words": words})
        if a.json:
            print(json.dumps(found, ensure_ascii=False, indent=2))
        else:
            for f in found:
                print(f'{f["path"]}:{f["line"]}  {f["term"]}  "{f["words"]}"')
        return 1 if a.strict and found else 0

    counts = {"linked": 0, "never": 0, "skipped": 0}
    total = sum(1 for _ in proposals(root, folder, skip, rules))
    style = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    width = shutil.get_terminal_size().columns - 4
    for i, (e, p, n, s, end) in enumerate(proposals(root, folder, skip, rules), start=1):
        lines = nfc(p.text).split("\n")
        old = lines[n - 1]
        mark = mark_for(e, old[s:end])
        new = old[:s] + mark + old[end:]
        print(f"{e['term']} · {i} of {total} · {p.path}:{n}")
        print("    " + in_context(old.strip(), s - (len(old) - len(old.lstrip())), end - (len(old) - len(old.lstrip())),
                                  mark, width, style))
        try:
            ans = input("Link? [y]es [n]ever here [s]kip [q]uit › ").strip().lower()[:1]
        except EOFError:
            print()
            ans = "q"
        if ans == "q":
            print()
            break
        if ans == "y":
            lines[n - 1] = new
            with open(p.file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            counts["linked"] += 1
        elif ans == "n":
            if a.skip:
                with open(a.skip, "a", encoding="utf-8") as f:
                    f.write(f"{p.path} | {e['term']}\n")
                print(f"  Saved to {a.skip}; won't ask again.")
            skip.add((p.path, e["term"]))
            counts["never"] += 1
        else:
            counts["skipped"] += 1
        print()
    print(f"{counts['linked']} linked, {counts['never']} never, {counts['skipped']} skipped. Review: git diff")
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
    c = sub.choices["candidates"]
    c.add_argument("--min-pages", type=int, default=2)
    c.add_argument("--common", default=COMMON, help="common words, one per line")
    k = sub.choices["link"]
    k.add_argument("--skip", help="the skip file of never pairs")
    k.add_argument("--check", action="store_true", help="list unmarked first mentions; write nothing")
    k.add_argument("--strict", action="store_true", help="with --check, exit 1 when any are found")
    a = ap.parse_args(argv)
    a.skip_section = a.skip_section or ["Ingredients"]
    if a.cmd == "link":
        return run_link(a)
    return run_candidates(a)


if __name__ == "__main__":
    sys.exit(main())
