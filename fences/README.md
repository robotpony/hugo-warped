# Fences

*Approved by Bruce, 2026-10-26. Shared by Not a Chef, warpedvisions.org (w42) and Scorekeep. It lives in this folder until it has a home of its own, and it links only within the folder, so it can move in one piece. Panels in `tabs` start with `tab:` lines (approved over `=== Label`). Open items are marked **Open** and tracked in `docs/PLAN.md` "Standard diagram fences".*

A fence is a code block with a type name, which a site or app draws as something richer: a diagram, a table, a box. Every project here embeds blocks this way, and only this way: no Hugo shortcodes, no `@` directive lines, no `> [!note]` callouts. The same block reads as plain text in Obsidian, on GitHub, and anywhere that can't draw it.

This page is the grammar every fence shares. Each type has its own page for its columns, rules and drawing (see "Fence types" at the end). A type page can narrow these rules, but it can't break them.

## Words used here

- **Type:** the name after the opening backticks (`formula`, `table`).
- **Target:** anything that reads fences: a Hugo site, the Scorekeep app, Obsidian, GitHub.
- **Hook:** a target's code for drawing one type. In Hugo, `layouts/_default/_markup/render-codeblock-<type>.html`.
- **MUST**, **MUST NOT**: required. Everything else describes how things work.

## Anatomy

````markdown
```table {name="card-values"}
K    | 0
A    | 1
2-10 | Face value
caption: Kings are free.
```
````

| Part | Here | Says |
|---|---|---|
| Type | `table` | Which hook draws it. Lowercase `a-z` and `-`. |
| Attributes | `{name="card-values"}` | Optional, in one `{…}` group after the type. See "Attributes". |
| Body | the four lines | What to draw, one line at a time. See "Lines". |

Nothing else goes on the opening line. Hugo drops bare words after the type without a warning (checked on Hugo 0.168), so an argument goes in an attribute or in the body:

````markdown
```diagram table hand          ← the hook sees only "diagram"
```

```diagram {draw="table hand"}  ← the hook sees draw = "table hand"
The table from above, then your hand up close.
```
````

## Kinds

Every type is one of four kinds. Its kind decides what the body has to say on its own.

**Diagram** (`formula`, `stack`, `timeline`, `flow`) draws something the prose around it already states. It MUST NOT add anything the text doesn't say, so a reader who can't see the drawing loses nothing.

````markdown
Reverse methods swap the order: cook gently first, then brown at the end.

```formula
oven        | Gentle | doneness
→ pan flame | Hot    | crust
```
````

**Data** (`table`, `reminders`) is the content itself, not a picture of it. Its plain text MUST be complete on its own.

````markdown
```reminders
Shuffle {decks} with {jokers} jokers.
```
````

**Placeholder** (`diagram`, `example`, `sheet`, `house-rules`) marks where a drawing goes that comes from somewhere else: the app's own code, a screenshot, a data file. Attributes say what to draw. The body is one plain line describing it, and it MUST NOT be empty. That line is what Obsidian and GitHub show, the web's alt text, and the app's VoiceOver label.

````markdown
```example {draw="golf-revealed"}
A hole's four hands turned face-up and totalled, the low one circled.
```
````

**Layout** (`tabs`) arranges ordinary Markdown: each part of the body is Markdown the page would show anyway, and the type sets it side by side or switchable. Its fallback is that Markdown as source text, in order, which MUST read clearly. Images don't preview there; the site's local preview is where a layout is checked.

`````markdown
````tabs {layout="side"}
tab: Pan
Fry in 1 cm of oil at 175°C, 4 to 5 minutes a side.

tab: Oven
Bake on a rack at 220°C for 25 minutes, turning once.
````
`````

## Lines

Whitespace at either end of a line is ignored, and blank lines are skipped. Every other line is a keyword line, a row, or a text line. Each type page says which of these it takes. (Layout types are the exception: between their keyword lines the body is block Markdown, blank lines and all.)

````markdown
```flow
row: Conventional                ← keyword line (starts a group)
Sear    | crust first            ← row: two cells
→ Oven  | cook through           ← row with a marker
row: Reverse
Oven    | cook through
→ Sear  | crust last
caption: Same steps, swapped     ← keyword line (trailer)
```
````

The `←` text on each line is a note: it's for whoever reads the source, and the hook drops it (see "Notes").

**Keyword line.** `key: value`. The key is lowercase `a-z` and `-`, starts the line, and is followed by a colon and a space. Each type lists the keywords it takes and where they go. Most go last, as a trailer (`caption:`, `bar:`, `repeat:`, `head:`). A few start a group (`flow`'s `row:`). Keywords are lowercase, so a row that starts with a capital is never read as one: `Note: salt early | brine` is a row.

`caption:` means the same thing in every type that takes it: one line, drawn under the block, last in the block.

**Row.** Cells split on `|` and trimmed, read **by position**: column 1 holds the same kind of thing in every row of that type. There's no header row and no `|---|` line. A type that needs printed column titles takes a `head:` keyword instead:

````markdown
```table {name="card-values"}
K    | 0
2-10 | Face value
head: Card | Worth
```
````

A row may stop early when its last cells are optional (`= patty | Patties | 6` leaves out `formula`'s swaps). A row with more cells than its type takes is a bad line.

**Marker.** A type may allow a marker at the start of a row, before column 1. The type page defines its markers:

| Type | Marker | Means |
|---|---|---|
| `formula` | `+`, `:`, `→`, `=` | How this slot joins the one before; `=` names the result |
| `timeline` | `~` | A faint entry: a detour or a tentative start |
| `flow` | `→` | Optional; the hook draws the arrows anyway |

**Text line.** Types with one value per line take the whole line as that value: a `timeline` entry, a `reminders` note, a placeholder's description.

````markdown
```timeline
1983 Atari BASIC
~2008 WordPress, a detour
2022 Hugo
```
````

### Notes

A note explains a line to whoever reads the source: why a value is what it is, where it came from, what to check. It's never drawn.

````markdown
```table {name="card-values"}
K    | 0           ← kings are free in our house
J Q  | 10 each
5 5  | Cancels to 0 ← pairs only; three of a kind still counts
caption: Kings are free.
```
````

- A note starts at `←` (or `<-`) with whitespace before it, or at the start of a line, and runs to the end of the line. The hook drops it and the whitespace before it, then reads what's left.
- A line that's only a note is skipped, like a blank line.
- Notes work on every line-read line: rows, text lines and keyword lines. A layout body (`tabs`) is ordinary Markdown, so notes don't apply there or inside a nested fence; Markdown has its own comments.
- To show a literal arrow in a cell, write `\←` (or `\<-`). The hook drops the backslash.
- A note is plain source text: it shows wherever the block isn't drawn (Obsidian, GitHub), and never in a drawing, its alt text or its `aria-label`.

`<-` is accepted for `←` as `->` is for `→`. No fence body in Not a Chef, w42 or Scorekeep held either arrow when notes were added (2026-10-26), so no existing line changes meaning. **Gap:** no hook strips notes yet. Until each project's hooks do, keep notes out of published content.

### Cells

Each type page says what each column holds. There are three sorts of cell:

| Sort | Holds | Example |
|---|---|---|
| Tokens | Space-separated keys from the type's own set: icon keys (`formula`), layer keys (`stack`), card ranks, suits and dice faces (`table`). A run is written `2-10`. | `crumbs egg`, `J Q`, `d5 d5 d5` |
| Inline text | Inline Markdown, rendered through the page's own hooks (in Hugo, `RenderString` with `"display" "inline"`), so each site's links and wiki links work. | `[[Pizza sauce]]`, `*optional*` |
| Plain text | Drawn exactly as written. | `Shuffle two decks.` |

A token cell that isn't all tokens is handled by its type page. In `formula` and `stack`, an unknown key draws a placeholder and warns. In `table`, a cell with no tokens at all is a word label (`Full house`).

## Attributes

Attributes carry what a plain-text reader doesn't need. The body MUST make sense with them stripped off. These are the shared keys:

| Key | Means | Values | Example |
|---|---|---|---|
| `name` | This block's id, so something else can ask for it. | Lowercase `a-z`, `0-9`, `-`. Unique within its file once a project's conditionals are resolved; lookups never cross files. | `{name="card-values"}`: Scorekeep's cheat sheet asks a game's page for this table. |
| `draw` | Which drawing a placeholder shows, from the drawings its target knows. Several words are an ordered list. | Lowercase words, space-separated. The type page lists them. | `{draw="table hand"}`: the table, then the hand. |
| `class` | A styling hint for one site. | Any. | `{class="warped-graph"}` |

`name` and `draw` do different jobs: `name` labels this block so it can be found, and `draw` picks something drawn elsewhere. Each type page says which keys it takes, and may define its own, like `tabs`'s `layout`. A type's own key means nothing on another type.

A hook ignores an attribute it doesn't know, without a warning, so content moves between projects without changes. A new shared key is added to this table first.

## Bad lines

A line that doesn't fit its type is skipped, with a warning. It never fails a site build. The warning names the type, quotes the line, says what was wanted, and gives the position:

````markdown
```flow
Sear | crust first
→ Oven | cook through | 30 min
Rest
```
````

```
WARN  flow: skipped "→ Oven | cook through | 30 min" (want "Label | note") in "…/steak.md:12:1"
```

That draws two steps, Sear then Rest. A warning means "not drawn this way yet", not "never valid": a later version of the type may give that line a meaning.

Some problems still draw, with a warning:

- An unknown token draws as a placeholder, in types that say so (`formula`, `stack`).
- Too many rows for the space still draw: `formula` over five slots, `flow` over five steps.
- A stray marker is dropped and the row draws (`→` on `flow`'s first step).

A block with no valid lines at all shows its source as preformatted text, plus a warning. It never draws nothing, so a reader still sees what was written. (w42's hooks draw nothing today; they change to match.)

A project can be stricter in its own checks. Scorekeep's `RulesDocumentTests` fail on any skipped line, because the app ships the same files. A hard stop like that belongs in a project's tests, or later in the shared validator, never in the site build.

## Where it can't be drawn

A target with no hook for a type shows the fence as preformatted text: Obsidian, GitHub, feed readers, another project's site. That's the intended fallback, and it's why bodies have to read well as plain text:

- Line up the pipes.
- Use words rather than codes where there's a choice.
- Give a `caption:` or description line that says what the drawing shows.

A target that has the hook may still fall back within it. Scorekeep's web hooks show a light and dark screenshot pair for a placeholder when one exists, and a dashed box with the description line when it doesn't.

An ordinary code block (```` ```bash ````, ```` ```json ````) isn't a fence, and a site never warns about one. A project may warn on an unknown type only where every block is expected to be a fence: Scorekeep's rules pages, where an unknown type is a plain `<pre>` and a warning on the site, and a test failure in the app, so it never ships.

## Project extensions

A project can add its own features around fences. They're outside this spec, and other projects don't need to support them.

**Conditionals around fences.** Scorekeep's `@if … @end` can wrap whole fences to pick one of two versions of a block. Both versions may share a `name`, since only one survives. A fence body is never conditional: no `@if` lines inside it. In this sketch the key and rows are made up:

````markdown
@if dice-extra = on
```table {name="score"}
d1 d1 d1 | 1,000
d5 | 50
```
@end
@if dice-extra = off
```table {name="score"}
d1 d1 d1 | 1,000
```
@end
````

**Value substitution.** Scorekeep fills `{key}` inside bodies before the fence is read, so `Shuffle {decks} with {jokers} jokers.` becomes `Shuffle 2 decks with 4 jokers.` The filled line must still follow the type's grammar.

**A source toggle.** w42 adds an (i) button that reveals a diagram's fenced source. A site may offer one; the spec doesn't require it.

## Drawing

Each project draws in its own hooks and CSS. No files are shared: the input is shared, and each type page records one project's rendering for reference when porting.

- Hooks write classes only, plus inline position variables where a layout needs them (`timeline`). Colours come from each theme's CSS.
- Class prefixes don't collide across projects: w42 uses `.tline-*` and `.flow-*`; Not a Chef uses `.formula`, `.f-*`, `.timeline` and `.tl-*`; Scorekeep uses `.sk-*`.

## Extending a type

A change to a shared type:

- is agreed by every project that uses it, and written in its type page first;
- keeps every line that's valid today drawing the same way;
- adds a new keyword, a new optional trailing column, or a new attribute, and never gives an old one a new meaning.

`flow`'s parallel rows are the model. `row:` was a new keyword, and a block without one still draws exactly as before. A counter-example: making `flow`'s second cell a duration instead of a note would redraw every existing block wrongly, so it would have to be a new keyword or a new type.

A new type starts in one project. It gets its own page here when a second project wants it, or when it's shared from the start.

## Fence types

| Type | Kind | Shape | Used by | Spec |
|---|---|---|---|---|
| `formula` | diagram | `icon | label | quantity | swaps`, operator marker; `caption:`, `bar:` | Not a Chef | `formula.md` |
| `stack` | diagram | `layer | label | role`, top first; `caption:`, `repeat:` | Not a Chef | `stack.md` |
| `timeline` | diagram | `YEAR Label` text lines, `~` marker | w42; Not a Chef (port pending) | `timeline.md` |
| `flow` | diagram | `Label | note`, optional `→` marker; `row:`, `caption:` | w42; Not a Chef (port pending) | `flow.md` |
| `table` | data | `tokens | text`; `head:`, `caption:`; `name` | Scorekeep (planned) | `table.md` |
| `reminders` | data | one note per text line | Scorekeep | `reminders.md` |
| `diagram`, `example` | placeholder | description line; `draw` | Scorekeep (planned) | `placeholders.md` |
| `sheet`, `house-rules` | placeholder | description line | Scorekeep (planned) | `placeholders.md` |
| `tabs` | layout | `tab: Label` then Markdown, per panel; `layout` | w42 (planned, replacing `{{< tabs >}}`), Not a Chef (wanted) | `tabs.md` |

Highlighted source isn't a fence type. w42's `qgraph` ASCII sketches (styled by one CSS rule, with no hook) and the `formula` block shown as source in w42's manifesto are ordinary code blocks. Nothing in this spec applies to a code block that no hook draws.

## Open

- **Charts.** Nobody needs a drawn chart yet. If one comes, the first shape on record is a labelled bar list (label, bar, note), from w42's `qgraph` sketch.
- **Home.** Every type's page lives in this folder (Bruce, 2026-10-26). `timeline.md` and `flow.md` came from w42's `themes/w42/docs/`, and `formula.md` and `stack.md` from `FORMAT.md`. The folder stays in Not a Chef for now and may move to a repo of its own.
- **Tools.** A validator any project can run on its Markdown, with the same checks the hooks warn on, plus a reference hook per type to port. In Not a Chef it would replace the build-time `warnf` checks and `/lint` item 5 as the source of truth.
