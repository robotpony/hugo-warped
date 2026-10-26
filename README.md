# hugo-warped

The Markdown dialect Bruce's Hugo sites share, and the Hugo plumbing that reads it.

Several sites embed richer things in plain Markdown: a recipe's ratio drawn as icons, a timeline of dates, a card game's scoring table. Each used to invent its own syntax (shortcodes, `@` lines, one-off code blocks). This repo holds the one shared way to write them, so the same source works on every site, in the Scorekeep app, and as readable text in Obsidian and on GitHub.

Sites share structure and parsing here. Each keeps its own look: nothing in this repo carries CSS, colours or drawing.

## Current state

*As of 2026-10-26.*

| Part | State |
|---|---|
| Fence spec (`fences/`) | **Approved** and in use. Nine fence types, a shared grammar, and a stable code for every warning. |
| Fixtures | Next. Shape agreed with Scorekeep; table, reminders and placeholders come first. |
| Validator | Planned, after the fixtures. |
| Hugo module | Planned. Parse partials only. |
| Plumbing and tools | Planned, as a second site needs each piece. |

There's no code here yet: the spec is the product so far, and each site's theme implements it in its own hooks. See `PLAN.md` for the open work.

## Fences

A fence is a fenced code block with a type name, which a site or app draws as something richer:

````markdown
```timeline
1983 Atari BASIC
~2008 WordPress, a detour
2022 Hugo
```
````

Where there's no hook for the type, the block shows as preformatted text, so the body is written to read well as plain text.

| Type | Kind | Used by |
|---|---|---|
| `formula`, `stack` | diagram | bruce-loves-to-cook.ca |
| `timeline`, `flow` | diagram | warpedvisions.org; the cookbook when a page needs one |
| `table`, `reminders` | data | Scorekeep |
| `diagram`, `example`, `sheet`, `house-rules` | placeholder | Scorekeep |
| `tabs` | layout | warpedvisions.org |

Start at `fences/README.md` for the shared grammar (lines, cells, notes, attributes, bad lines and warning codes). Each type has its own page beside it.

## Users

| Site | Repo | Theme or parser | Status |
|---|---|---|---|
| bruce-loves-to-cook.ca | `~/writing/not-a-chef` | Fugu (`robotpony/hugo-theme-fugu`) | Implements `formula` and `stack`, notes included |
| warpedvisions.org | `~/projects/sites/w42` | w42 theme 0.7.2 | Implements `timeline`, `flow` and `tabs`, with warning codes; the tabs shortcode is being removed |
| Scorekeep | `~/projects/utilities/scorekeep` | Swift `RulesDocument` and the `site/` hooks | Migrating from `@` placeholders; its parser is being rewritten to the spec |

Other sites (space-command.ca, brucealderson.ca, robotpony.ca, w31, w32, warped-next) hold only ordinary code blocks, which the spec never touches.

## Planned

In priority order. A piece moves in when a second project needs it.

1. **Fixtures and validator.** Good and bad sample blocks per type (`fences/fixtures/<type>/<case>.md` beside its expected `.json`), the source of truth for every parser. Then a stdlib Python validator any project can run on its Markdown.
2. **Hugo module.** Optional, with one parse partial per fence type that returns data and warnings; each theme draws its own HTML. An example site runs the fixtures through Hugo. Later: link, image, heading and table hooks.
3. **Plumbing.** Mounting a project's `docs/` as site pages, content adapters, JSON indexes.
4. **Tools.** Shared build and content tools, such as `compare-builds.py`, `frontmatter.py` and `drafts.py` from Fugu.

## Changing the spec

A change to a shared type is agreed by every project that uses it and written in its type page before any code, and nothing valid today may change how it draws (`fences/README.md`, "Extending a type"). Propose changes to the hugo-warped agent, or open an issue.

## Out of scope

Themes, CSS and look; browser JS (warped.js); the H⌘ Obsidian plugin (`robotpony/warped-hugo`, being deprecated, and a different project despite the name).
