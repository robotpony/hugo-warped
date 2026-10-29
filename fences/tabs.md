# The tabs block

*Approved 2026-10-26. Designed with warped-agent (w42 content); replaces w42's `{{< tabs >}}` and `{{< tab >}}` shortcodes.*

A fenced code block with the info string `tabs` shows the same thing two or more ways: source beside the page it makes, or a method beside its variation. It's a **layout** fence (`README.md`, "Kinds"): each panel is ordinary Markdown, and the block reads as that Markdown in order where it isn't drawn. Used by w42 (two blocks in the manifesto, both shortcodes today), and wanted by Not a Chef.

The reference hook will be w42's `layouts/_default/_markup/render-codeblock-tabs.html`, writing the same HTML as today's shortcode (`themes/w42/layouts/shortcodes/tabs.html`), so `tabs.css` doesn't change.

## Syntax

`````markdown
````tabs {layout="side"}
tab: Pan
Fry in 1 cm of oil at 175°C, 4 to 5 minutes a side.

tab: Oven
Bake on a rack at 220°C for 25 minutes, turning once.
````
`````

1. **Panel.** A `tab: <label>` keyword line starts a panel, and everything up to the next `tab:` (or the end) is its body. The label is inline Markdown. A `← note` on a `tab:` line is dropped, as on any keyword line (`README.md`, "Notes"); in a body it's ordinary text. The block MUST start with a `tab:` line.
2. **Body.** Block Markdown, rendered with the page's own `RenderString` and `"display" "block"`, so each site's hooks apply: images and page resources, links, wiki links, lists, headings, other fences. Blank lines inside a body are kept; this is the one type whose body isn't read line by line.
3. **Layout.** The `layout` attribute: `side` shows every panel at once as equal columns on wide screens, falling back to tabs where columns would be too narrow; `stack` shows every panel at once, full width, one under another, each under its label; `aside` stacks the panels the same way in a narrow column on the right, with the text that follows wrapping beside it on wide screens, and full width like `stack` where the column would be too narrow. Without `layout`, the panels are switchable tabs, the first one open. The width and gutter of an `aside` are the site's.

## Aside

*Approved 2026-10-29, at Bruce's request via warped-agent, for the Bruce burger block in w42's cookbook post. w42 is the only site drawing `tabs` today; Not a Chef and Fugu take it up when a page needs one.*

`aside` is for a block that sits beside the prose rather than between it: a recipe's source next to a tall screenshot of the page it makes. It changes placement only, so a reader without the hook loses nothing. The block goes before the paragraphs meant to wrap beside it. Before this, `aside` warned `unknown-layout` and drew as switchable tabs, so no valid block draws differently.

`````markdown
````tabs {layout="aside"}
tab: Text
```stack
…
```

tab: On the site
![The Bruce burger's build, drawn on the site](bruce-burger-build.png)
````
`````

## Nesting

A panel can hold another fence. The outer fence MUST use more backticks than any fence inside it (CommonMark's own rule). Inside a nested fence, `tab:` lines are part of that fence, not panel breaks:

``````markdown
`````tabs {layout="stack"}
tab: Text
````markdown
## Mechanic

A roux is equal parts fat and flour by weight.

```formula
butter flour | Roux   | 1
: water      | Liquid | 5
```
````

tab: On the site
![The gravy recipe, with the 1:5 roux formula drawn in its sidebar](gravy-recipe.png)
`````
``````

Here the Text panel holds a four-backtick `markdown` fence, which itself holds a three-backtick `formula`, so the outer `tabs` fence takes five.

## Use

- Two or three panels, about six at most (`tabs.css` handles six).
- Labels are short: "Text", "On the site", "Pan", "Oven".
- Each panel should make sense alone; a reader without the hook reads them one after another.

## Lines that don't match

```
WARN  tabs: skipped "Some text" (want "tab: Label" first) in "…/index.md:56:1"
```

These warn:

- Text before the first `tab:` line: skipped. `out-of-order`
- A `tab:` line with no label: drawn with the label "Tab". `missing-label`
- A panel with an empty body: drawn empty. `empty-group`
- An unknown `layout`: drawn as switchable tabs. `unknown-layout`
- More than six panels: drawn, with a warning. `over-limit`
- No `tab:` lines at all: the source shows as preformatted text, as for every type. `no-valid-lines`

## Rendering in w42

Not part of the spec; for reference when porting.

- No JS. Switchable tabs are a radio per panel, the first checked, and `common/tabs.css` shows the panel matching the checked one. Arrow keys move between tabs, as in any radio group.
- `layout="stack"` draws no radios: each label is a plain caption over its panel.
- `layout="aside"` (theme 0.11.0) draws as `stack` in a 260px column floated right with a 24px left gutter, from 700px up; the next h2–h4 clears it. Under 700px it's full-width `stack`.
- Classes: `.tabs`, `.tabs.side`, `.tabs.stack`, `.tabs.stack.aside`, `.tabs-input`, `.tabs-label`, `.tabs-panel`, with `--tabs` set to the panel count.
- The shortcode stays until both manifesto blocks are migrated and checked against the live page; it's removed in a later theme bump.
