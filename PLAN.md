# Plan

Open work for hugo-warped. The fence spec's history before 2026-10-26 is in Not a Chef's `docs/PLAN.md` ("Standard diagram fences"); everything since is in this repo's git log.

## Done

As of 2026-10-26: the spec in `fences/`, with warning codes and every reading the fixtures needed settled; fixtures for all eleven types and the page checks (`fences/fixtures/`, 111 cases); the validator (`tools/check-fences.py`), which Not a Chef's `/lint` runs; the Hugo module's parse partials (`layouts/partials/hugo-warped/`), tested in Hugo against every block fixture; and `tools/run-hugo-fixtures.py`, which w42 (0.7.5) and Fugu pass. As of 2026-10-27 the cookbook reads every fence through the module: Fugu main 82ce85f imports it pinned at 4045b3f, and Not a Chef main cd43dc4 takes it by submodule with the module replacement, checked on Hugo 0.166 and 0.168. w42 followed the same day: theme master 707cf36 (0.8.0) imports it pinned at 4045b3f, and site main de4b7dd takes it by submodule with the replacement (not yet deployed).

## Open

Here:

- [ ] Charts: open in the spec, none needed yet. The first shape on record is a labelled bar list, from w42's `qgraph` sketch.
- [ ] Later, when a second site needs them: link, image, heading and table hooks.

Other agents:

- [ ] Fugu ports `timeline` and `tabs`, when a page needs one (fugu-agent).
- [ ] w42 removes the `tabs` shortcode (w42 theme agent).
- [ ] Scorekeep's parser and hooks drop `←` notes, and `RulesDocument` is rewritten to the spec against its vendored fixtures (Scorekeep content agent).

## Plumbing and tools

Moved in when a second project needs them: mounting a project's `docs/` as site pages, content adapters, JSON indexes (Not a Chef's `recipes/index.json`, Scorekeep's `rules.json`), Fugu's `compare-builds.py`, `frontmatter.py` and `drafts.py`, and `~/projects/sites/hugo-auto-drafts-and-future-posts`.
