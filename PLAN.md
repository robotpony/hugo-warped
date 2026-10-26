# Plan

Open work for hugo-warped. The fence spec's history before 2026-10-26 is in Not a Chef's `docs/PLAN.md` ("Standard diagram fences"), which also lists what the spec changes on each site.

## Setup

- [x] Import the fence spec with its history into `fences/` (2026-10-26), and qualify its references to Not a Chef's files.
- [x] Send the spec's path to the not-a-chef content agent, warped-agent and the Scorekeep content agent.
- [x] Create the GitHub remote: https://github.com/robotpony/hugo-warped (2026-10-26).

## Fences

- [ ] Fixtures (table, reminders, placeholders, page checks and formula done 2026-10-26; stack, timeline, flow and tabs next): good and bad sample blocks per type, each with its expected parse and warnings. They're the source of truth for every parser: the validator, the Hugo partials, and Scorekeep's Swift `RulesDocument`. Shape agreed with the Scorekeep content agent (2026-10-26): `fences/fixtures/<type>/<case>.md` (one whole fence) beside `<case>.json` (type, kind, attributes, lines numbered from the opening fence as 1, warnings, fallback); notes stripped in the expected output; typed tokens for cells; project extensions left out; `fences/fixtures/VERSION` holds the date and spec commit, since Scorekeep vendors a copy. Table, reminders and placeholders come first.
- [x] Warning codes (approved 2026-10-26): shared codes in `fences/README.md` "Warning codes", type codes beside each page's "Lines that don't match". Parsers compare codes and line numbers, never message text.
- [ ] Validator: stdlib Python, run on any project's Markdown, with the same checks the hooks warn on. In Not a Chef it replaces the build-time `warnf` checks and the `/lint` command's item 5.
- [ ] Charts: open in the spec, none needed yet. The first shape on record is a labelled bar list, from w42's `qgraph` sketch.

Spec work that other agents build:

- [ ] `←` notes: Scorekeep's parser and hooks drop them. w42 (theme 0.6.0) and Fugu (1d97f5f) are done.
- [x] Fugu's formula hook warns on a row with more than four cells (1d97f5f).
- [ ] Fugu's formula hook adds the checks settled in de2df26: `stray-marker`, `missing-cell` (row skipped), `out-of-order` after `=` or the trailer, `duplicate-keyword`, and `over-limit` on icons and swaps (fugu-agent). `fences/fixtures/formula/` has a case for each.
- [ ] Fugu ports of `timeline`, `flow` and `tabs`, when a page needs one (fugu-agent).
- [ ] w42 removes the `tabs` shortcode (w42 theme agent).

## Hugo module

- [ ] One parse partial per fence type, returning data and warnings; themes draw their own HTML.
- [ ] An example site that runs the fixtures through the partials, so they can't drift from the validator.
- [ ] Later, when a second site needs them: link, image, heading and table hooks.

## Plumbing and tools

Moved in when a second project needs them: mounting a project's `docs/` as site pages, content adapters, JSON indexes (Not a Chef's `recipes/index.json`, Scorekeep's `rules.json`), Fugu's `compare-builds.py`, `frontmatter.py` and `drafts.py`, and `~/projects/sites/hugo-auto-drafts-and-future-posts`.

## After the remote exists

- [x] Send the repo URL to fugu-agent, which then links `fences/formula.md` and `stack.md` from Fugu's `docs/recipe-format.md` and `docs/features.md`.
