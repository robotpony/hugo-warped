# Plan

Open work for hugo-warped. The fence spec's history before 2026-10-26 is in Not a Chef's `docs/PLAN.md` ("Standard diagram fences"), which also lists what the spec changes on each site.

## Setup

- [x] Import the fence spec with its history into `fences/` (2026-10-26), and qualify its references to Not a Chef's files.
- [x] Send the spec's path to the not-a-chef content agent, warped-agent and the Scorekeep content agent.
- [x] Create the GitHub remote: https://github.com/robotpony/hugo-warped (2026-10-26).

## Fences

- [x] Fixtures (every type done 2026-10-26): good and bad sample blocks per type, each with its expected parse and warnings. They're the source of truth for every parser: the validator, the Hugo partials, and Scorekeep's Swift `RulesDocument`. Shape agreed with the Scorekeep content agent (2026-10-26): `fences/fixtures/<type>/<case>.md` (one whole fence) beside `<case>.json` (type, kind, attributes, lines numbered from the opening fence as 1, warnings, fallback); notes stripped in the expected output; typed tokens for cells; project extensions left out; `fences/fixtures/VERSION` holds the date and spec commit, since Scorekeep vendors a copy. Table, reminders and placeholders come first.
- [x] Warning codes (approved 2026-10-26): shared codes in `fences/README.md` "Warning codes", type codes beside each page's "Lines that don't match". Parsers compare codes and line numbers, never message text.
- [x] Validator: `tools/check-fences.py`, stdlib Python, run on any project's Markdown, with the same checks the hooks warn on plus the page checks. `tools/test-check-fences.py` compares its parse of all 111 fixtures in full.
- [x] Not a Chef's `/lint` item 5 runs the validator (1807a72). Fugu's hooks keep their own build warnings, as the spec expects of a hook.
- [ ] Charts: open in the spec, none needed yet. The first shape on record is a labelled bar list, from w42's `qgraph` sketch.

Spec work that other agents build:

- [ ] `←` notes: Scorekeep's parser and hooks drop them. w42 (theme 0.6.0) and Fugu (1d97f5f) are done.
- [x] Fugu's formula hook warns on a row with more than four cells (1d97f5f).
- [x] Fugu's formula hook adds the checks settled in de2df26 and a2926dc (6cad03b, 5d0d729): `stray-marker`, `missing-cell` (row skipped), `out-of-order` after `=` or the trailer, `duplicate-keyword`, and `over-limit` on icons and swaps (fugu-agent). `fences/fixtures/formula/` has a case for each.
- [x] Fugu's stack hook adds the checks settled in cb7ef71 (405ace9): `missing-cell` (row skipped, no key as label), `too-many-cells`, `out-of-order` after the trailer, `duplicate-keyword` on a second caption, and `bad-repeat` for a count under 2 or not a number and for a backwards range (fugu-agent). `fences/fixtures/stack/` has a case for each.
- [x] Fugu's port of `flow` (5f21797), first used on Cornmeal fried chicken.
- [x] Fugu's flow hook passes all 17 flow fixtures at ffc4258 (4d08907).
- [x] w42's flow hook adds the checks settled in ffc4258 (theme 0.7.4, 48a4edc; all 26 timeline and flow fixtures pass): `unknown-keyword` for a keyword line flow doesn't take (skipped, not drawn as a step), and `duplicate-keyword` for a second `caption:` (the first stands). w42's timeline hook gives `unknown-keyword`, not `bad-year`, for a keyword line (w42 theme agent). `fences/fixtures/flow/` and `timeline/` have a case for each.
- [ ] Fugu ports of `timeline` and `tabs`, when a page needs one (fugu-agent).
- [ ] w42 removes the `tabs` shortcode (w42 theme agent).
- [x] w42's tabs hook drops a `← note` on a `tab:` line (638b870), and passes `fences/fixtures/tabs/` (theme 0.7.5, 2adc2d7).

## Hugo module

- [x] One parse partial per fence type, returning data and warnings; themes draw their own HTML. `partials/hugo-warped/parse.html` dispatches by type and `warn.html` prints the warnings; `go.mod` makes the repo importable.
- [x] An example site that runs the fixtures through the partials, so they can't drift from the validator: `tools/test-hugo-partials.py` builds one and compares every block fixture's parse in full (106 cases; `table/bad-attributes` can't be seen in Hugo). `tools/run-hugo-fixtures.py` (from the w42 theme agent) already builds the fixtures through a theme's hooks and checks warnings, fallback and what's drawn; w42 0.7.5 passes all 40 timeline, flow and tabs cases.
- [ ] Later, when a second site needs them: link, image, heading and table hooks.

## Plumbing and tools

Moved in when a second project needs them: mounting a project's `docs/` as site pages, content adapters, JSON indexes (Not a Chef's `recipes/index.json`, Scorekeep's `rules.json`), Fugu's `compare-builds.py`, `frontmatter.py` and `drafts.py`, and `~/projects/sites/hugo-auto-drafts-and-future-posts`.

## After the remote exists

- [x] Send the repo URL to fugu-agent, which then links `fences/formula.md` and `stack.md` from Fugu's `docs/recipe-format.md` and `docs/features.md`.
