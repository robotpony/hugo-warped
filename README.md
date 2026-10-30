# hugo-warped

The Markdown dialect my Hugo sites share, and the Hugo plumbing that reads it.

Several of my sites embed richer things in plain Markdown: a recipe's ratio drawn as icons, a timeline of dates, a card game's scoring table. Each site grew its own syntax for these (shortcodes, `@` lines, one-off code blocks), and none of them read well outside the site that drew them. This repo holds one shared way to write them, so the same source works on every site, in the Scorekeep app, and as readable text in Obsidian and on GitHub.

The sites share structure and parsing here. Each keeps its own look, so nothing in this repo carries CSS, colours or drawing.

## Where it stands

*As of 2026-10-30.*

| Part | State |
|---|---|
| Fence spec (`fences/`) | **Approved** and in use. Eleven fence types, a shared grammar, and a stable code for every warning. |
| Fixtures (`fences/fixtures/`) | **Done** for every type. Fugu passes formula, stack and flow; w42 passes timeline, flow and tabs. |
| Validator (`tools/check-fences.py`) | **Done.** Stdlib Python, run on any project's Markdown. It passes every fixture (`tools/test-check-fences.py`), and Not a Chef, w42 and Scorekeep check clean. |
| Hugo module (`layouts/partials/hugo-warped/`) | **Done**, and optional. One parse partial per type, returning the same parse as the validator. It passes every block fixture in Hugo (`tools/test-hugo-partials.py`). Fugu and w42 read every fence through it, pinned at 4045b3f. |
| Glossary (`glossary/`) | **Approved** 2026-10-30, for Not a Chef first. An entry per file, wiki-link marks, partials for the list, lookups and `index.json`, and `tools/glossary.py` to suggest terms and mark them. Fixtures pass in Python and Hugo. |
| Plumbing and tools | `tools/run-hugo-fixtures.py` runs the fixtures through a theme's hooks. The rest comes as a second site needs each piece. |

The spec and its fixtures are the product. Each theme reads fences with the module's partials and draws them in its own hooks; Scorekeep implements the spec in Swift. `PLAN.md` has the open work.

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

## The glossary

A site's glossary is a folder of entries, one Markdown file per term, and a word in the text is marked as a plain wiki link, `[[Deglaze|deglaze]]`, so Obsidian follows it too. The partials build the A–Z list, resolve a mark to its entry, and write `index.json`; `tools/glossary.py` suggests terms worth defining and marks first mentions, asking before each one. `glossary/README.md` is the spec. Not a Chef uses it first; w42 has no wiki links and isn't touched by it.

## Where it's used

| Site | Repo | Theme or parser | Status |
|---|---|---|---|
| bruce-loves-to-cook.ca | `~/writing/not-a-chef` | Fugu (`robotpony/hugo-theme-fugu`) | Draws `formula`, `stack` and `flow` through the module, and cuts long gaps in its lineage timelines |
| warpedvisions.org | `~/projects/sites/w42` | w42 theme 0.11.0 | Draws `timeline`, `flow` and `tabs` through the module, and zooms clustered timeline dots; the tabs shortcode is gone |
| Scorekeep | `~/projects/utilities/scorekeep` | Swift `RulesDocument` and the `site/` hooks | Moving from `@` placeholders to fences, with its parser rewritten to the spec |

My other sites (space-command.ca, brucealderson.ca, robotpony.ca, w31, w32, warped-next) only hold ordinary code blocks, which the spec never touches.

## The Hugo module

A theme can read fences with the module's partials and draw them its own way. Hugo 0.168 is what I test with.

### Adding it to a project

The theme whose hooks call the partials owns the dependency, not the site: it imports hugo-warped as a Hugo Module. One theme config then serves both ways a site can take the theme.

**In the theme** (Fugu, say), import it in `hugo.toml`, and pin it in the theme's `go.mod` as you would Blowfish:

```toml
[[module.imports]]
path = "github.com/robotpony/hugo-warped"
```

```text
require github.com/robotpony/hugo-warped v0.0.0-<date>-<commit>
```

Don't use `theme = ["hugo-warped"]` in the theme. In module mode a bare name only resolves from the site's `themes/` folder, so module sites fail to build.

**A site that takes the theme as a Hugo Module** needs nothing more: Hugo fetches hugo-warped at the theme's pin.

**A site that takes the theme as a git submodule** (my sites do) adds hugo-warped beside it, pinned to a commit, and maps the module path to that folder:

```sh
git submodule add https://github.com/robotpony/hugo-warped themes/hugo-warped
```

```toml
theme = ["fugu", "blowfish"]

[module]
replacements = "github.com/robotpony/hugo-warped -> hugo-warped"
```

Without the replacement, Hugo looks for `themes/github.com/robotpony/hugo-warped` and the config fails to load. I tested both kinds of site on Hugo 0.168.

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

## Licence

MIT, like Fugu, so anyone can use it. See `LICENSE`. The one exception is `tools/data/common-en.txt`, a word list from wordfreq under CC BY-SA 4.0 (`tools/data/README.md`).
