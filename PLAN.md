# Plan

Open work for hugo-warped. Finished work is in this repo's git log; the spec's history before 2026-10-26 is in Not a Chef's git log (`docs/PLAN.md`, `docs/fences/`).

## Done

As of 2026-10-27: the spec in `fences/` with fixtures for all eleven types (111 cases), the validator (`tools/check-fences.py`, run by Not a Chef's `/lint`), the Hugo module's parse partials, and `tools/run-hugo-fixtures.py`. Fugu (82ce85f) and w42 (theme 0.8.0, 707cf36) read every fence through the module, pinned at 4045b3f; both sites take it by submodule with the module replacement. w42 removed its `tabs` shortcode (theme 236b8bd).

## Open

Here:

- [ ] Charts: open in the spec, none needed yet. The first shape on record is a labelled bar list, from w42's `qgraph` sketch.
- [ ] Later, when a second site needs them: link, image, heading and table hooks.

Other agents:

- [ ] Fugu ports `timeline` and `tabs`, when a page needs one (fugu-agent).
- [ ] Fugu's lineage zooms on clustered years, per `fences/timeline.md` "Clusters": built in Fugu ffa1a1d (sidebar gap 22px, body 6%), waiting on Bruce's preview of /methods/chicken-sandwiches/ and a push (fugu-agent). #focus
- [ ] w42 checks whether its timelines cluster, and if so adds the same zoom and records its dot gap (w42 theme agent; not running when the rule landed, so not yet told).
- [ ] w42 deploys the module move (site main de4b7dd; warped-agent).
- [ ] Scorekeep's parser and hooks drop `←` notes, and `RulesDocument` is rewritten to the spec against its vendored fixtures (Scorekeep content agent).

## Plumbing and tools

Moved in when a second project needs them: mounting a project's `docs/` as site pages, content adapters, JSON indexes (Not a Chef's `recipes/index.json`, Scorekeep's `rules.json`), Fugu's `compare-builds.py`, `frontmatter.py` and `drafts.py`, and `~/projects/sites/hugo-auto-drafts-and-future-posts`.
