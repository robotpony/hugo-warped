# Fences

*Draft, 2026-10-26. Shared by Not a Chef, warpedvisions.org (w42) and Scorekeep. It lives in this folder until it has a home of its own, and it links only within the folder, so it can move in one piece. Open items are marked **Open** and tracked in `docs/PLAN.md` "Standard diagram fences".*

A fence is a code block with a type name, which a site or app draws as something richer: a diagram, a table, a box. Every project here embeds blocks this way, and only this way: no Hugo shortcodes, no `@` directive lines, no `> [!note]` callouts. The same block reads as plain text in Obsidian, on GitHub, and anywhere that can't draw it.

This page is the grammar every fence shares. Each type has its own page for its columns, rules and drawing (see "Fence types" at the end). A type page can narrow these rules, but it can't break them.

## Review #todo

Bruce, tick to approve, or write a change after the item.

- [ ] Three kinds of fence: **diagram** (illustrates the prose, carries nothing it doesn't say), **data** (is the content, complete as plain text), **placeholder** (drawn from elsewhere; the body is one plain description line, never empty). See "Kinds".
- [ ] The shared line grammar: keyword lines are lowercase `key: value`; rows are `|` cells read by position, with no header row (`head:` when a type needs printed titles); markers before column 1; a row with too many cells is a bad line. See "Lines".
- [ ] Attributes: `name` (this block's id, unique within its file once conditionals are resolved, so two `@if` versions of one table can share it; `table.md`), `draw` (which drawing a placeholder shows, kept apart from `name`), `class` (one site's styling hint). Unknown keys are ignored silently. See "Attributes".
- [ ] A block with no valid lines shows its source as preformatted text, never nothing. w42's hooks change to match, and so does the formula hook's extra-cell gap (`formula.md`). See "Bad lines".
- [ ] Project extensions stay outside the spec: Scorekeep's `@if` may wrap whole fences but never sits inside a body, `{key}` substitution runs before parsing, and w42's (i) source toggle is optional. See "Project extensions".
- [ ] Card and dice tokens in `table.md`: die faces written `d1`–`d6` (easy to type) rather than `⚀`–`⚅` (pictures in plain text, but hard to type and tiny), `Joker` as a token, and `stack:7♣` for the topped stack (a plainer spelling is welcome). See `table.md`, "Tokens".
- [ ] Tabs: design it next, with a longer outer fence (```` ````tabs ````) so a tab can hold another fence. See "Open".

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

Every type is one of three kinds. Its kind decides what the body has to say on its own.

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

## Lines

Whitespace at either end of a line is ignored, and blank lines are skipped. Every other line is a keyword line, a row, or a text line. Each type page says which of these it takes.

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

The `←` notes are labels for this page, not part of the block.

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

`name` and `draw` do different jobs: `name` labels this block so it can be found, and `draw` picks something drawn elsewhere. Each type page says which keys it takes.

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

A type no hook knows is a plain `<pre>` and a warning on a site. Scorekeep bundles its Markdown into the app, so there an unknown type fails the project's tests and never ships.

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
| `tabs` | **Open** | text beside a picture or source, replacing w42's `{{< tabs >}}` | w42, Not a Chef (both waiting) | to design |

Highlighted source isn't a fence type. w42's `qgraph` ASCII sketches (styled by one CSS rule, with no hook) and the `formula` block shown as source in w42's manifesto are ordinary code blocks. Nothing in this spec applies to a code block that no hook draws.

## Open

- **Tabs.** No syntax yet. The hard case is a tab that holds another fence (the manifesto's tabs hold ```` ```markdown ```` and ```` ```formula ````), so the outer fence needs longer backticks (```` ````tabs ````) or another way to embed source.
- **Charts.** Nobody needs a drawn chart yet. If one comes, the first shape on record is a labelled bar list (label, bar, note), from w42's `qgraph` sketch.
- **Home.** Every type's page lives in this folder (Bruce, 2026-10-26). `timeline.md` and `flow.md` came from w42's `themes/w42/docs/`, and `formula.md` and `stack.md` from `FORMAT.md`. The folder stays in Not a Chef for now and may move to a repo of its own.
- **Tools.** A validator any project can run on its Markdown, with the same checks the hooks warn on, plus a reference hook per type to port. In Not a Chef it would replace the build-time `warnf` checks and `/lint` item 5 as the source of truth.
