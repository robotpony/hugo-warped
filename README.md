# hugo-warped

The Markdown dialect Bruce's Hugo sites share, and the Hugo plumbing that reads it. Sites share structure and parsing here; each keeps its own look, so nothing in this repo carries CSS, colours or drawing.

## What's here

- `fences/`: the fence spec, the shared grammar for embedded blocks (`formula`, `stack`, `timeline`, `flow`, `table`, `reminders`, the placeholders and `tabs`). Start at `fences/README.md`.

## Planned

In priority order. A piece moves in when a second project needs it.

1. **Fences.** Fixtures (good and bad sample blocks with their expected parse and warnings) and a validator any project can run (stdlib Python).
2. **Hugo module.** Optional, with one parse partial per fence type that returns data and warnings; each theme draws its own HTML. An example site runs the fixtures through Hugo. Later: link, image, heading and table hooks.
3. **Plumbing.** Mounting a project's `docs/` as site pages, content adapters, JSON indexes.
4. **Tools.** Shared build and content tools, such as `compare-builds.py`, `frontmatter.py` and `drafts.py` from Fugu.

## Users

| Site | Repo | Fences |
|---|---|---|
| bruce-loves-to-cook.ca | `~/writing/not-a-chef` (Fugu theme) | formula, stack |
| warpedvisions.org | `~/projects/sites/w42` (w42 theme) | timeline, flow, tabs |
| Scorekeep | `~/projects/utilities/scorekeep` (iOS app and `site/`) | table, reminders, placeholders |

## Out of scope

Themes, CSS and look; browser JS (warped.js); the H⌘ Obsidian plugin (`~/projects/sites/warped-hugo`, deprecated, a different project despite the name).
