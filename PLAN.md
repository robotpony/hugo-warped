# Plan

Open work for hugo-warped. Finished work is in this repo's git log; the spec's history before 2026-10-26 is in Not a Chef's git log.

## Here

- [ ] Charts: none needed yet. The first shape on record is a labelled bar list, from w42's `qgraph` sketch.
- [ ] Link, image, heading and table hooks, when a second site needs them.
- [ ] Plumbing, as a second project needs each piece: mounting `docs/` as site pages, content adapters, JSON indexes (`recipes/index.json`, `rules.json`), Fugu's `compare-builds.py`, `frontmatter.py` and `drafts.py`, and `~/projects/sites/hugo-auto-drafts-and-future-posts`.

## Other agents

- [ ] Not a Chef bumps `themes/hugo-warped` to 4d260ae, so its 24 stub entries stay out of the list and linking until they're written (Not a Chef content agent).
- [ ] Fugu draws the glossary through the partials at 4d260ae: render-link's popover, the list page with search, `index.json` (fugu-agent, briefed by bruce-loves-to-cook commander).
- [ ] Scorekeep drops `←` notes and rewrites `RulesDocument` to the spec against its vendored fixtures (Scorekeep content agent).
- [ ] Fugu ports `timeline` and `tabs` when a page needs one (fugu-agent).
- [ ] Not a Chef, Fugu and w42 delete their merged `hugo-warped-module` branches: Not a Chef's local one, Fugu's local and remote, and w42's local and remote (both merged into w42 main as of 2026-10-30) (Not a Chef content agent, fugu-agent, w42 theme agent).
