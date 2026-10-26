# Fences

*Draft, 2026-10-26. Shared by Not a Chef, warpedvisions.org (w42) and Scorekeep, and kept in this folder until it has a home of its own; it links only within the folder, so it can move as a whole. Open items are marked **Open** and tracked in `docs/PLAN.md` "Standard diagram fences".*

## Review #todo

Bruce, tick to approve, or write a change after the item.

- [ ] Three kinds of fence: **diagram** (illustrates the prose, carries nothing it doesn't say), **data** (is the content, complete as plain text), **placeholder** (drawn from elsewhere; the body is one plain description line, never empty). See "Kinds".
- [ ] The shared line grammar: keyword lines are lowercase `key: value`; rows are `|` cells read by position, with no header row (`head:` when a type needs printed titles); markers before column 1; a row with too many cells is a bad line. See "Lines".
- [ ] Attributes: `name` (this block's id, unique within its file once conditionals are resolved, so two `@if` versions of one table can share it; `table.md`), `draw` (which drawing a placeholder shows, kept apart from `name`), `class` (one site's styling hint). Unknown keys are ignored silently. See "Attributes".
- [ ] A block with no valid lines shows its source as preformatted text, never nothing. w42's hooks change to match, and so do the formula hook's extra-cell gap (`formula.md`). See "Lines that don't match".
- [ ] Project extensions stay outside the spec: Scorekeep's `@if` may wrap whole fences but never sits inside a body, `{key}` substitution runs before parsing, and w42's (i) source toggle is optional. See "Project extensions".
- [ ] Card and dice tokens in `table.md`: die faces written `d1`–`d6` (easy to type) rather than `⚀`–`⚅` (pictures in plain text, but hard to type and tiny), `Joker` as a token, and `stack:7♣` for the topped stack (a plainer spelling is welcome). See `table.md`, "Tokens".
- [ ] Tabs: design it next, with a longer outer fence (```` ````tabs ````) so a tab can hold another fence. See "Open".

A fence is a named code block that a site or app draws as something richer: a diagram, a table, a box. Every project here embeds blocks this way, and only this way: no Hugo shortcodes, no `@` directive lines, no `> [!note]` callouts. A fence reads as plain text in Obsidian, on GitHub, and anywhere without a hook, and it draws where there is one.

This file is the grammar every fence shares. Each fence type has its own page for its columns and drawing (see "Fence types" below). A fence page can narrow these rules, but it can't break them.

## Anatomy

````markdown
```table {name="card-values"}
K    | 0
A    | 1
2-10 | Face value
caption: Pairs only.
```
````

1. **Type.** The word after the backticks: lowercase, `a-z` and `-`. It picks the hook (`render-codeblock-<type>.html` in Hugo).
2. **Attributes.** Optional, in one `{…}` group after the type: `{key="value" key2="value"}`. See "Attributes".
3. **Body.** Lines, read one at a time. See "Lines".

Nothing else goes on the opening line. Hugo drops any bare words after the type without a warning (checked on Hugo 0.168: in ```` ```diagram table hand ````, the hook sees only `diagram`). An argument goes in an attribute or in the body.

## Kinds

Every type is one of three kinds, and its kind decides what the body must say on its own:

- **Diagram** (`formula`, `stack`, `timeline`, `flow`): draws something the prose on the page already states. It MUST NOT carry anything the text doesn't say, so losing the drawing loses nothing.
- **Data** (`table`, `reminders`): the block is the content. Its plain text MUST be complete on its own.
- **Placeholder** (`diagram`, `sheet`, `example`, `house-rules`): the drawing comes from somewhere else: an app's own code, a screenshot, a data file. Attributes pick what to draw. The body is one plain line describing it. That line is what a reader without the hook sees, the web's alt text and placeholder text, and an app's VoiceOver label. A placeholder is never empty, because an empty fence reads like a mistake.

## Lines

Leading and trailing whitespace on a line is ignored, and blank lines are skipped. Each remaining line is one of three kinds:

1. **Keyword line.** `key: value`, where `key` is lowercase `a-z` and `-`, starting the line, and followed by a colon and a space. Each fence type lists the keywords it takes and says where they may go. Most take them as a trailer, after every row (`caption:`, `bar:`, `repeat:`, `head:`); a few use one to start a group (`flow`'s `row:`). Because keywords are lowercase, a row that starts with a capital (`Note: …`) is never read as one.
2. **Row.** Cells split on `|`, trimmed, read **by position**: column 1 is always the same thing in every row of that type. There's no header row and no `|---|` line (a type that needs printed column titles takes a `head:` keyword). A row may stop early when its last cells are optional. A row with more cells than its type takes is a bad line.
3. **Text line.** Types with one value per line (`timeline`, `reminders`, a placeholder's description) take the whole line as their one cell.

A type may also allow a **marker** at the start of a row, before column 1: `formula`'s operator (`+`, `:`, `→`), `timeline`'s `~`, and `flow`'s optional `→`. The fence page defines its markers.

`caption:` means the same thing in every type that takes it: one line, drawn under the block, last in the block.

### Cells

Each fence page says what each column holds:

- **Tokens.** Space-separated keys from the type's own set: icon keys (`formula`), layer keys (`stack`), card ranks, suits and dice faces (`table`). A run is written `2-10`. The fence page says what happens to a cell that isn't all tokens: it draws a placeholder and warns (`formula`, `stack`), or it's read as a word label (`table`'s "Full house").
- **Inline text.** Inline Markdown, rendered through the page's own render hooks (in Hugo, `RenderString` with `"display" "inline"`), so each site's link handling applies.
- **Plain text.** Drawn as written.

## Attributes

Attributes are for things a reader of the plain text doesn't need. The body must make sense with them stripped off. These are the shared keys:

| Key | Means | Values |
|---|---|---|
| `name` | This block's id, so something else can ask for it (Scorekeep's cheat sheet asks a game's page for its `card-values` table). | Lowercase `a-z`, `0-9`, `-`. Unique within its file once a project's conditionals are resolved (two `@if` branches may each hold a version of the same block); lookups never cross files. |
| `draw` | Which drawing a placeholder shows, from the drawings its target knows (`draw="golf-revealed"`). Several words are an ordered list (`draw="table hand"`: the table, then the hand). | Lowercase words, space-separated. The fence page lists them. |
| `class` | A presentation hint for one site. | Any. Other sites ignore it. |

`name` and `draw` are different things: `name` labels this block, while `draw` picks something drawn elsewhere. A fence page says which keys its type takes.

A hook ignores an attribute it doesn't know, without warning, so content stays portable. A new shared key gets added to this table first.

## Lines that don't match

A bad line is skipped and warned about. It never fails a site build. The warning names the type, quotes the line, says what was wanted, and gives the position:

```
WARN  flow: skipped "A | b | c" (want "Label | note") in "…/index.md:30:1"
```

A warning means "not drawn this way yet", not "never valid".

Recoverable problems draw anyway and warn: an unknown token (as a placeholder, where the type says so), too many rows for the space (`formula` over five slots, `flow` over five steps), or a stray marker.

A block with no valid lines at all shows its source as preformatted text, plus the warning, never nothing. (w42's hooks draw nothing today; they change to match.)

A project can be stricter than its site build: Scorekeep's `RulesDocumentTests` fails on any skipped line, since the app ships the same files. Hard stops belong in a checker like that, or in the shared validator later, not in the site build.

## Where it can't be drawn

A target with no hook for a type shows the fence as preformatted text. That includes Obsidian, GitHub, feed readers, and another project's site. That's the designed fallback, and it's why bodies have to read well as plain text: aligned pipes, words rather than codes where possible, and a `caption:` or description line that says what the drawing shows.

A target that has the hook may still fall back within it. Scorekeep's web hooks show a light and dark screenshot pair for a placeholder when one exists, and a dashed box with the description line when it doesn't.

An unknown type is a plain `<pre>` and a warning on a site. In an app that bundles its Markdown (Scorekeep), an unknown type fails that project's tests, so it never ships.

## Project extensions

A project can add things around fences that are its own, outside this spec:

- **Conditionals around fences.** Scorekeep's `@if … @end` can wrap whole fences to pick between two versions of a block. A fence body is never conditional: no conditional lines inside it.
- **Value substitution.** Scorekeep fills `{key}` inside bodies (```` ```reminders ```` uses `{decks}`) before the fence is read. The result must still follow the type's grammar.
- **A source toggle.** w42 adds an (i) button that reveals a diagram's fenced source. A site may offer one; the spec doesn't require it.

## Drawing

Each project draws in its own hook and CSS, with no shared files. What's shared is the input; each fence page records one project's rendering for reference when porting. Hooks write classes only (plus inline position variables where a layout needs them, like `timeline`), and colours come from each theme's CSS. Class prefixes don't collide across projects: w42 uses `.tline-*` and `.flow-*`; Not a Chef uses `.formula`, `.f-*`, `.timeline` and `.tl-*`; Scorekeep uses `.sk-*`.

## Extending a type

A change to a shared type:

- is agreed by every project that uses it, and written in its fence page first;
- keeps every line that's valid today drawing the same way;
- uses a new keyword, a new optional trailing column, or a new attribute, never a new meaning for an old one.

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

Not fence types: highlighted source shown as an example, like w42's `qgraph` ASCII sketches (styled by one CSS rule, no hook) and the `formula` block shown as source in w42's manifesto. A language name that no hook draws is just a code block, and nothing in this spec applies to it.

## Open

- **Tabs.** No syntax yet. The hard case is that a tab holds another fence (the manifesto's tabs hold ```` ```markdown ```` and ```` ```formula ````), so the outer fence needs longer backticks (```` ````tabs ````) or another way to embed source.
- **Charts.** Nobody needs a drawn chart yet. If one comes, the first shape on record is a labelled bar list (label, bar, note), from w42's `qgraph` sketch.
- **Home.** Every type's page lives in this folder (Bruce, 2026-10-26); `timeline.md` and `flow.md` came from w42's `themes/w42/docs/`, and `formula.md` and `stack.md` from `FORMAT.md`. The folder stays in Not a Chef for now and may move to a repo of its own.
- **Tools.** A validator any project can run on its Markdown, with the same checks the hooks warn on, plus a reference hook per type to port. Here it would replace the build-time `warnf` checks and `/lint` item 5 as the source of truth.
