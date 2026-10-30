# The glossary

*Approved 2026-10-30, at Bruce's request, with hugo-warped as its home. Designed by Not a Chef (`docs/PLAN.md`, "Concepts", and `mockups/glossary.html`), which uses it first.*

A glossary is a list of a site's concepts, one short definition each, with the words in the text that name them marked as links. This page sets how entries are written, how a mark is written and found, and what the partials and tools return. How any of it looks is each site's own.

The glossary isn't a fence. It shares the fence spec's rules where they apply: warnings never fail a build, and Obsidian only needs to show clear source text.

## Entries

An entry is one Markdown file in the site's glossary folder. Not a Chef's is `content/reference/glossary/`; a site names its own when it calls the partials and tools. The folder's `_index.md` is the glossary page, and every other page in it is an entry.

```markdown
---
title: Deglaze
also: [deglazing, deglazed]
date: 2026-10-30
---

Pour a liquid into a hot pan and scrape, so the browned bits stuck to the bottom dissolve into it. Wine, stock, beer, or water all work; the liquid only has to lift the [[Fond|fond]].
```

1. **Term.** `title` is the term, as the list shows it. It MUST be set.
2. **Other forms.** `also` lists the other forms a mark or a tool may match: plurals, verb forms, a short name ("Kewpie" for "Kewpie mayonnaise"). A YAML list, flow (`[a, b]`) or block (`- a`). It is not `aliases`, which Hugo turns into redirects.
3. **Date.** `date`, as on any page.
4. **Definition.** The body is the definition, in block Markdown, and may mark other terms. Its **short form** is the first sentence of its first paragraph, as plain text: what a hover shows and what `index.json` carries. A sentence ends at the first `.`, `!` or `?` (with any closing quote or bracket) followed by a space or the paragraph's end; a paragraph with none is all one sentence. So the first sentence SHOULD stand alone, and SHOULD avoid abbreviations like "e.g.".
5. **No page each.** Entries build into the list only. The glossary page's front matter cascades it to them:

   ```yaml
   cascade:
     target: {kind: page}
     build: {render: never, list: always}
   ```

### Keys and anchors

- An entry's **keys** are its term and each `also` form, matched by their **match key**: lowercase, every run of characters other than letters and digits made one space, and trimmed. "Rich veg/mushroom stock" and "rich veg mushroom stock" are the same key; so are curly and straight apostrophes.
- Its **anchor**, the id on the glossary page, is the term lowercased with every run of characters other than letters and digits made one `-`, trimmed of `-`: `deglaze`, `kewpie-mayonnaise`, `msg`. Its url is the glossary page's url plus `#` and the anchor.
- Its **letter** is the first character of its match key, uppercased, or `#` when that isn't a letter. The list is sorted by match key.

## Marks

A mark is a plain wiki link, as Obsidian writes it, so Obsidian shows and follows it too:

- `[[Deglaze]]`: the link text is the target.
- `[[Deglaze|deglaze]]`: the target, then the text shown. In a table cell the pipe is escaped, `[[Deglaze\|deglaze]]`, as Obsidian does.

A mark **resolves** to the entry with a key equal to the target's match key. A hand-written mark and a tool-written one are the same.

A site's own pages can be wiki-link targets too (Not a Chef links recipes by title). The site decides the order, and SHOULD try its pages first and the glossary second, as Not a Chef does, so a concept with its own essay links there.

Wiki links are part of the glossary, not of the fence dialect. A site with no glossary doesn't need them: w42 doesn't use them, and nothing here changes how it draws.

### Where a mark counts

Marks are read from a page's Markdown, outside its front matter. A mark counts in prose, and doesn't count:

- in a code span (`` `[[Fond]]` ``);
- in a fenced block, unless it's a `tabs` fence, whose panels render as Markdown. A fence inside a panel is read the same way. A fence closes at a line of the same character, at least as long, with nothing after it.

## Warnings

As with fences, a warning names the problem and the file, and never fails a build.

- An entry with no `title`: skipped. `missing-title`
- An entry with an `aliases` key: built as usual, with a warning, since Hugo makes redirects of it. `aliases-not-also`
- An entry with an empty body: listed, with no short form. `empty-definition`
- Two entries sharing a key: the first by file path keeps it. `duplicate-key`
- A mark that resolves to nothing: drawn as the site draws a broken link. `unresolved-mark`

## The list

The glossary page lists every entry A to Z, grouped by letter. Each entry carries its term, other forms, definition, anchor and **used in**: the pages, outside the glossary folder, with a mark that resolves to it, sorted by title. Used-in comes from the build, so it never needs writing by hand.

A site can add entries that aren't files in the folder, such as Not a Chef's reference essays ("Win the fridge"), which have pages of their own. Each gives a term, its other forms, a short form and a url, and is listed and resolved like any other.

`index.json`, for other tools and sites, is the list as a JSON array, sorted the same way:

```json
[{"term": "Deglaze", "also": ["deglazing", "deglazed"], "def": "Pour a liquid into a hot pan and scrape, so the browned bits stuck to the bottom dissolve into it.", "url": "/reference/glossary/#deglaze"}]
```

## The partials

In `layouts/partials/hugo-warped/glossary/`, optional like the fence partials. `glossary` is the glossary page's path (`"/reference/glossary"`), and `extra` the site's added entries, as dicts of `term`, `also`, `def` and `url`; both are taken by every partial.

| Partial | Takes | Returns |
|---|---|---|
| `entries.html` | `(dict "glossary" … "extra" …)` | Every entry, sorted: dicts of `term`, `also`, `key` (the term's match key), `keys` (every key it holds), `anchor`, `letter`, `def`, `url`, and `page` (the entry's page, or nil for an added one). |
| `resolve.html` | `(dict "glossary" … "extra" … "target" "deglazing")` | The entry whose key matches the target, or `false`. |
| `list.html` | `(dict "glossary" … "extra" …)` | Letters in order: dicts of `letter` and `entries`, each entry with `used` (its used-in pages) added. |
| `index.html` | `(dict "glossary" … "extra" …)` | The `index.json` array, ready for `jsonify`. |
| `marks.html` | a page | The page's marks, in order: dicts of `target` and `text`. |

`entries.html` caches its work once per build and argument, so a render hook can call `resolve.html` on every mark.

## The tools

`tools/glossary.py`, stdlib Python like the validator. It writes nothing unless asked, and asks before every change.

### `candidates`

```sh
tools/glossary.py candidates CONTENT --glossary reference/glossary
```

Suggests words to define: each word or phrase on at least two pages (`--min-pages`), outside the glossary folder, that isn't already a key, and is either rare in everyday English or set in italics. Rare means not in `tools/data/common-en.txt`, the 25,000 most common English words from wordfreq. A common word counts as italic only when it's written lowercase in italics on at least as many pages, so a label like *Notes* doesn't. Phrases come only from italics (*mise en place*), and their words count only as the phrase. A word only ever written capitalised is taken as a name and left out. Words are read from prose as marks are, also skipping link targets, URLs and the Ingredients sections `link` skips (`--skip-section`).

A word's forms are grouped under the one on the most pages, by a rough stem: one common suffix off (`-s`, `-ed`, `-ing`, `-ion`, `-ify`, …), keeping at least four letters. It's a suggestion, so a stray group (*patties* with *patted*) is fine. It prints a ranked list, by pages and then by word, and `--json` prints the same as data; the site files them where it keeps its review notes:

```
  pages  word
     33  deglaze
     27  emulsify  (emulsion, emulsified)
      2  mise en place  (italics)
```

### `link`

```sh
tools/glossary.py link CONTENT --glossary reference/glossary --skip tools/glossary-skip.txt
tools/glossary.py link CONTENT --glossary reference/glossary --skip tools/glossary-skip.txt --check
```

For each entry, A to Z, and each page that has no mark for it yet, finds the first mention of any of its keys in prose: whole words, any case, the longest key first where two start together. It doesn't look in front matter, headings, links (Markdown, wiki or HTML) or URLs, code spans, fenced blocks (a `tabs` panel is prose), or a section headed "Ingredients" (`--skip-section`, repeatable), down to the next heading at its level or above, so its component lists are skipped too. The entry's own file and the glossary page are left out.

Each mention is shown as a diff and asked: `[y]es`, `[n]ever on this page`, `[s]kip for now`, or `[q]uit`. Yes writes `[[Term]]` when the words match the term exactly, otherwise `[[Term|words]]`. Never adds a line to the skip file, and the pair isn't asked again. Skip asks again next run.

The skip file is one pair per line, the page's path under `CONTENT`, a space, `|`, a space, and the term; `#` starts a comment:

```
essays/food-memories/camp-cooking.md | Fond
```

`--check` lists every first mention not yet marked or skipped, as `path:line  Term  "words"`, and writes nothing, for a site's lint. It exits 0, or 1 with `--strict` when it finds any.

It matches words, not meaning, which is why it asks: Camp cooking's "fond memories" matches Fond.

## Fixtures

`glossary/fixtures/` holds the cases every reader of this page is checked against: the tools (`tools/test-glossary.py`) and the partials in Hugo (`tools/test-hugo-glossary.py`).

- `site/`: a small content folder with a glossary, pages and a skip file.
- `extra.json`: an added entry, as a site passes `extra`.
- `entries.json`: what `entries.html` returns for the site, without `page`. The tools check the fields but `def` and `url`, which only Hugo makes.
- `list.json`, `index.json`: what `list.html` (used-in as page paths) and `index.html` return, with `extra.json` added.
- `resolve.json`: targets and the term each resolves to, or null.
- `marks.json`: the marks read from each page, with the file line the tools report.
- `warnings.json`: each entry problem, by path and code.
- `link-check.txt`: what `link --check` prints.
- `linked/`: each page after answering yes to every question.
- `candidates.txt`: what `candidates` prints.

## History

Not a Chef's glossary began as one page, `content/reference/glossary.md`, with an entry per `## ` heading, which Fugu's link hook split on. This spec replaces it with a file per entry (decided 2026-10-30).
