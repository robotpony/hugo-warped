# Plan

Open work for hugo-warped. Finished work is in this repo's git log; the spec's history before 2026-10-26 is in Not a Chef's git log.

## Here

- [ ] Charts: none needed yet. The first shape on record is a labelled bar list, from w42's `qgraph` sketch.
- [ ] Link, image, heading and table hooks, when a second site needs them.
- [ ] Plumbing, as a second project needs each piece: mounting `docs/` as site pages, content adapters, JSON indexes (`recipes/index.json`, `rules.json`), Fugu's `compare-builds.py`, `frontmatter.py` and `drafts.py`, and `~/projects/sites/hugo-auto-drafts-and-future-posts`.

## Other agents

- [ ] Scorekeep drops `←` notes and rewrites `RulesDocument` to the spec against its vendored fixtures (Scorekeep content agent).
- [ ] Fugu ports `timeline` and `tabs` when a page needs one (fugu-agent).
- [ ] Fugu and w42 delete their merged `hugo-warped-module` branches: Fugu's on origin (local deleted 2026-10-30; waiting on Bruce's go-ahead in fugu-agent's session), and w42's local and remote (both merged into w42 main as of 2026-10-30) (fugu-agent, w42 theme agent).
