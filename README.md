# hugo-warped

The Markdown dialect my Hugo sites share, and the Hugo plumbing that reads it.

Several of my sites embed richer things in plain Markdown: a recipe's ratio drawn as icons, a timeline of dates, a card game's scoring table. Each site grew its own syntax for these (shortcodes, `@` lines, one-off code blocks), and none of them read well outside the site that drew them. This repo holds one shared way to write them, so the same source works on every site, in the Scorekeep app, and as readable text in Obsidian and on GitHub.

The sites share structure and parsing here. Each keeps its own look, so nothing in this repo carries CSS, colours or drawing.

## Where it stands

*As of 2026-10-26.*

| Part | State |
|---|---|
| Fence spec (`fences/`) | **Approved** and in use. Nine fence types, a shared grammar, and a stable code for every warning. |
| Fixtures (`fences/fixtures/`) | **Done** for every type. Fugu passes formula, stack and flow; w42 passes timeline, flow and tabs. |
| Validator (`tools/check-fences.py`) | **Done.** Stdlib Python, run on any project's Markdown. It passes every fixture (`tools/test-check-fences.py`), and Not a Chef, w42 and Scorekeep check clean. |
| Hugo module | Planned. Parse partials only. |
| Plumbing and tools | `tools/run-hugo-fixtures.py` runs the fixtures through a theme's hooks. The rest comes as a second site needs each piece. |

The spec and its fixtures are the product so far, and each site's theme implements them in its own hooks. `PLAN.md` has the open work.

## Fences

A fence is a fenced code block with a type name, which a site or app draws as something richer:

````markdown
```timeline
1983 Atari BASIC
~2008 WordPress, a detour
2022 Hugo
```
````

Where there's no hook for the type, the block shows as preformatted text. So I write every body to read well as plain text, too.

| Type | Kind | Used by |
|---|---|---|
| `formula`, `stack` | diagram | bruce-loves-to-cook.ca |
| `timeline`, `flow` | diagram | warpedvisions.org, and the cookbook when a page needs one |
| `table`, `reminders` | data | Scorekeep |
| `diagram`, `example`, `sheet`, `house-rules` | placeholder | Scorekeep |
| `tabs` | layout | warpedvisions.org |

Start at `fences/README.md` for the shared grammar: lines, cells, notes, attributes, bad lines and warning codes. Each type has its own page beside it.

## Where it's used

| Site | Repo | Theme or parser | Status |
|---|---|---|---|
| bruce-loves-to-cook.ca | `~/writing/not-a-chef` | Fugu (`robotpony/hugo-theme-fugu`) | Implements `formula` and `stack`, with notes and warning codes (Fugu 9fc6950) |
| warpedvisions.org | `~/projects/sites/w42` | w42 theme 0.7.3 | Implements `timeline`, `flow` and `tabs`, with warning codes; the tabs shortcode is on its way out |
| Scorekeep | `~/projects/utilities/scorekeep` | Swift `RulesDocument` and the `site/` hooks | Moving from `@` placeholders to fences, with its parser rewritten to the spec |

My other sites (space-command.ca, brucealderson.ca, robotpony.ca, w31, w32, warped-next) only hold ordinary code blocks, which the spec never touches.

## What's next

In rough priority order. A piece moves in here once a second project needs it.

1. **Fixtures and validator.** Good and bad sample blocks for each type (`fences/fixtures/<type>/<case>.md`, with the expected `.json` beside it). They're the source of truth for every parser. Then a stdlib Python validator that any project can run on its Markdown.
2. **Hugo module.** Optional, with one parse partial per fence type that returns data and warnings. Each theme still draws its own HTML. An example site runs the fixtures through Hugo. Later: link, image, heading and table hooks.
3. **Plumbing.** Mounting a project's `docs/` as site pages, content adapters, JSON indexes.
4. **Tools.** Shared build and content tools, like `compare-builds.py`, `frontmatter.py` and `drafts.py` from Fugu.

## Changing the spec

Every project that uses a type agrees to a change first, and it's written in the type's page before any code. Nothing that's valid today may change how it draws (`fences/README.md`, "Extending a type"). Open an issue to propose one.

## Not in scope

Themes, CSS and the look of each site, and browser JS (warped.js).
