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
| Hugo module (`layouts/partials/hugo-warped/`) | **Done**, and optional. One parse partial per type, returning the same parse as the validator. It passes every block fixture in Hugo (`tools/test-hugo-partials.py`). No theme uses it yet. |
| Plumbing and tools | `tools/run-hugo-fixtures.py` runs the fixtures through a theme's hooks. The rest comes as a second site needs each piece. |

The spec and its fixtures are the product so far. Each site's theme implements them in its own hooks, and a new theme can start from the module's partials instead. `PLAN.md` has the open work.

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
| bruce-loves-to-cook.ca | `~/writing/not-a-chef` | Fugu (`robotpony/hugo-theme-fugu`) | Implements `formula`, `stack` and `flow`, passing their fixtures (Fugu 2380c23) |
| warpedvisions.org | `~/projects/sites/w42` | w42 theme 0.7.5 | Implements `timeline`, `flow` and `tabs`, passing their fixtures; the tabs shortcode is on its way out |
| Scorekeep | `~/projects/utilities/scorekeep` | Swift `RulesDocument` and the `site/` hooks | Moving from `@` placeholders to fences, with its parser rewritten to the spec |

My other sites (space-command.ca, brucealderson.ca, robotpony.ca, w31, w32, warped-next) only hold ordinary code blocks, which the spec never touches.

## The Hugo module

A theme can read fences with the module's partials and draw them its own way. Hugo 0.168 is what I test with.

### Adding it to a project

The theme whose hooks call the partials owns the dependency, not the site. A site that uses the theme only has to provide the checkout. Otherwise a second site on the same theme ends up with missing partials and no clue why.

**As a git submodule.** I use this for my sites, because they already get their themes this way:

1. In the site, add hugo-warped beside the theme, pinned to a commit:

   ```sh
   git submodule add https://github.com/robotpony/hugo-warped themes/hugo-warped
   ```

2. In the theme's own `hugo.toml` (Fugu's, say), list it as a component:

   ```toml
   theme = ["hugo-warped"]
   ```

   Hugo finds it in the site's `themes/` folder. The site's theme list keeps naming only its own themes (`["fugu", "blowfish"]`), without hugo-warped.

**As a Hugo Module**, for a project that already uses them (it needs Go). In the theme's config:

```toml
[[module.imports]]
path = "github.com/robotpony/hugo-warped"
```

Either way:

- Pin to a commit, never a moving `main`. When you bump it, run `tools/run-hugo-fixtures.py` against the theme first, so a spec change can't reach a site unchecked.
- Don't copy the partials into a theme. Copies drift from the fixtures, which is what this repo is here to stop.

Scorekeep doesn't use the partials: its Swift parser vendors `fences/fixtures/` and compares its copy against `fences/fixtures/VERSION`.

### Using it in a hook

In a hook such as `layouts/_default/_markup/render-codeblock-flow.html`:

```go-html-template
{{- $p := partial "hugo-warped/parse.html" . -}}
{{- partial "hugo-warped/warn.html" (dict "hook" . "parse" $p) -}}
{{- if $p.fallback }}<pre><code>{{ .Inner }}</code></pre>{{ else }}…draw $p.lines…{{ end -}}
```

The parse has the shape of `fences/fixtures/<type>/<case>.json`. To check `formula` or `stack` keys, pass them: `(dict "hook" . "keys" (dict "formula" $iconKeys))`. The partials live under `partials/hugo-warped/`, so they never collide with a theme's own `partials/fences/`.

## What's next

In rough priority order. A piece moves in here once a second project needs it.

1. **Shared hooks.** Link, image, heading and table hooks, when a second site needs them.
2. **Plumbing.** Mounting a project's `docs/` as site pages, content adapters, JSON indexes.
3. **Tools.** Shared build and content tools, like `compare-builds.py`, `frontmatter.py` and `drafts.py` from Fugu.

## Changing the spec

Every project that uses a type agrees to a change first, and it's written in the type's page before any code. Nothing that's valid today may change how it draws (`fences/README.md`, "Extending a type"). Open an issue to propose one.

## Not in scope

Themes, CSS and the look of each site, and browser JS (warped.js).
