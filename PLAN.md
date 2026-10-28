# Plan

Open work for hugo-warped. Finished work is in this repo's git log; the spec's history before 2026-10-26 is in Not a Chef's git log.

## Here

- [ ] Charts: none needed yet. The first shape on record is a labelled bar list, from w42's `qgraph` sketch.
- [ ] Link, image, heading and table hooks, when a second site needs them.
- [ ] Plumbing, as a second project needs each piece: mounting `docs/` as site pages, content adapters, JSON indexes (`recipes/index.json`, `rules.json`), Fugu's `compare-builds.py`, `frontmatter.py` and `drafts.py`, and `~/projects/sites/hugo-auto-drafts-and-future-posts`.

## Other agents

- [ ] w42 deploys the module move (site main de4b7dd; warped-agent).
- [ ] w42 checks whether its timelines cluster, and if so adds the zoom and records its dot gap (w42 theme agent; not yet told).
- [ ] Scorekeep drops `←` notes and rewrites `RulesDocument` to the spec against its vendored fixtures (Scorekeep content agent).
- [ ] Fugu ports `timeline` and `tabs` when a page needs one (fugu-agent).
- [ ] Not a Chef and Fugu delete their merged `hugo-warped-module` branches (Not a Chef content agent, fugu-agent).
