# The flow block

A fenced code block with the info string `flow` draws a short sequence of steps as one row, with arrows between them, or up to three parallel rows to compare. It's a **diagram** fence (`README.md`, "Kinds"), shared by warpedvisions.org (the w42 theme) and bruce-loves-to-cook.ca (the Fugu theme), and specified here since 2026-10-26 (it began in w42's `themes/w42/docs/`). Each site keeps its own hook and CSS; the syntax below is what both accept. It's modelled on the cookbook's `formula` diagrams in their `→` mode, without icons.

The reference hook is w42's `layouts/_default/_markup/render-codeblock-flow.html`. It hands the block to `layouts/partials/diagrams/flow.html`, which draws it (CSS in `assets/css/common/flow.css`), by way of `layouts/partials/diagram.html`, which adds an (i) toggle to the fenced source. The toggle is w42's, not part of the spec.

## Syntax

````markdown
```flow
Markdown | in git
Hugo
public/
rsync
Dreamhost
caption: How a post gets to the server
```
````

One step per line, in order:

1. **Label.** Everything before the `|`, or the whole line when there's no `|`. Keep it to one or two short words.
2. **Note.** Optional: everything after the `|`. It's drawn under the label, quieter than the label.
3. **Arrow prefix.** Lines after the first may start with `→ ` or `-> `, which is dropped; the hook draws the arrows itself. This lets a cookbook formula sequence paste in once its icon column is removed:

   ````markdown
   ```flow
   Roast    | deep brown
   → Extract  | bones set the time
   → Reduce   | by half
   → Strain
   ```
   ````

4. **Caption.** An optional `caption: <text>` line, last in the block, is drawn under the row (or under all the rows). It uses the same keyword as `formula`.

Leading and trailing whitespace around a line, a label or a note is ignored, and blank lines are skipped. Labels, notes, row labels and the caption are inline Markdown, rendered with the page's own `RenderString` and `"display" "inline"`, so each site's render hooks apply.

Keep a block to about five steps. More still draw, with a warning, since they crowd the row.

## Parallel rows

`row:` lines split a block into rows drawn one above the other, to set two or three sequences side by side:

````markdown
```flow
row: 1983
Tape | eats the game
Notebook | the design
Rebuild
row: 2026
Session | ends, forgets
CLAUDE.md | the design
Rebuild
caption: Same lesson, about 40 years apart
```
````

1. **Row.** `row: <label>` starts a row, and the steps under it, up to the next `row:` or the caption, belong to it. The label is optional (`row:` alone is fine) and is inline Markdown. On wide screens it's drawn at the row's left; on narrow ones, as a small heading above the row.
2. **All or nothing.** A block that uses `row:` must start with one; a step before it warns and isn't drawn. A block with no `row:` line is one row, exactly as above.
3. **Columns.** Steps line up by position: step 3 of every row is in the same column. Rows may differ in length; a shorter row just ends, with no placeholder. Identical labels in different rows stay separate steps.
4. **Arrows.** A leading `→ ` or `-> ` is dropped on any step line. On a row's first step it's dropped with a warning, as on a block's first line.
5. **Caption.** One `caption:` line, last, after every row, covers the whole block. A `row:` after it warns.
6. **Limits.** Up to three rows, and about five steps in each. More still draw, with a warning.

## Use

The diagram illustrates the text; it MUST NOT replace it. Only draw a sequence the surrounding prose already states. The block has to read as plain text where it's written (Obsidian, GitHub), which this syntax does.

## Accessibility

The row reads as one image, with an `aria-label` that names the steps in order, each label followed by its note and joined by ", then ": "Markdown in git, then Hugo, then public/, then rsync, then Dreamhost". The caption is a real `figcaption`, outside that image.

Parallel rows are one `<ol>` each, in one wrapper with the caption. Each row's `aria-label` leads with its label: "1983: Tape eats the game, then Notebook the design, then Rebuild". A row without a label reads as the steps alone.

## Lines that don't match

A line that doesn't match isn't drawn. The hook prints a build warning that quotes the line and gives the block's position:

```
WARN  flow: skipped "A | b | c" (want "Label | note") in "…/index.md:30:1"
```

These warn:

- More than one `|`: `A | b | c`
- No label: `| a note`
- A step or `row:` after the caption: the caption goes last
- An arrow on the first line (`→ Markdown`), or on a row's first step: the arrow is dropped and the step is drawn, with a warning
- More than five steps in a row: drawn, with a warning
- A step before the first `row:`, in a block that uses rows: not drawn
- A `row:` with no steps: not drawn
- More than three rows: drawn, with a warning
- No steps at all: the source shows as preformatted text, as for every type (`README.md`, "Lines that don't match"). **Gap:** w42's hook draws nothing today.

A warning means "not drawn this way yet", not "never valid". Any extension (parallel rows were one; branches or step links would be others) must be agreed between both sites and written here first, and must keep every line that's valid today drawing the same way.

## Rendering in w42

Not part of the spec; for reference when porting.

- Classes all start with `flow` (`.flow`, `.flow-row`, `.flow-step`, `.flow-label`, `.flow-note`, `.flow-arrow`, `.flow-cap`, and for rows `.flow-rows`, `.flow-grid`, `.flow-head`, `.flow-item`), so they don't collide with the cookbook's `.formula` / `.f-*`. The hook writes classes only; colours come from each theme's CSS.
- Each label sits in a small box (`--entry` fill, `--tertiary` border) in Lora, with its note under it in italic `--secondary`. The arrows are `--series-ink`, level with the boxes. The caption is centred under the row in `--secondary`. These are the timeline's tokens, so dark mode follows the theme.
- Parallel rows share one CSS grid: the row labels in the first column (small, monospace, `--secondary`, right-aligned), and each row's `<ol>` a subgrid across the rest, so columns line up whatever the label widths. An item after the first holds its arrow and its step.
- At 640px and below, a single row becomes a centred column with the arrows pointing down. Parallel rows stack instead, each label centred above its row and the row wrapping as needed; columns don't line up there.
