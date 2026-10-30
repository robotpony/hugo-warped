# Plan

Open work for hugo-warped. Finished work is in this repo's git log; the spec's history before 2026-10-26 is in Not a Chef's git log.

## Here

- [ ] Charts: none needed yet. The first shape on record is a labelled bar list, from w42's `qgraph` sketch.
- [ ] Link, image, heading and table hooks, when a second site needs them.
- [ ] Plumbing, as a second project needs each piece: mounting `docs/` as site pages, content adapters, JSON indexes (`recipes/index.json`, `rules.json`), Fugu's `compare-builds.py`, `frontmatter.py` and `drafts.py`, and `~/projects/sites/hugo-auto-drafts-and-future-posts`.

## Other agents

- [ ] Scorekeep drops `←` notes and rewrites `RulesDocument` to the spec against its vendored fixtures, in five steps: vendor and test the fixtures, rewrite the parser, migrate the 11 pages, read tables by name, and point its README at the spec. Due 2026-10-31, before release work (SCOREKEEP).
- [ ] Fugu ports `timeline` and `tabs` when a page needs one (fugu-agent).
- [ ] w42 deletes its merged `hugo-warped-module` branches, local and remote (both merged into w42 main as of 2026-10-30), once Bruce agrees (w42 theme agent).
