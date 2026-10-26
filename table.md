# The table block

A fenced code block with the info string `table` holds a short reference table: cards or dice on the left, what they're worth or do on the right. It's a **data** fence (`README.md`, "Kinds"): the block is the content, and its plain text is complete on its own. Used by Scorekeep, whose iOS app and Hugo site both read the same `docs/rules/<game>.md` files; the app's cheat sheet asks a game's page for a table by name. Specified here since 2026-10-26 (it replaces Scorekeep's `@table <name>` placeholders, whose rows lived in Swift).

## Syntax

````markdown
```table {name="card-values"}
K    | 0
A    | 1
2-10 | Face value
J Q  | 10 each
5 5  | A matched pair in the same column cancels to 0
Joker | −2
caption: Kings are free; pairs only, so a third matching card still counts.
```
````

One row per line, two cells, read by position (`README.md`, "Lines"):

1. **Tokens.** What the row is about, drawn as small cards, dice or suits (see "Tokens"). A cell that isn't tokens is a word label (see "Word labels").
2. **Text.** What it's worth or does. Inline Markdown, rendered through the page's own hooks.

Trailer keywords, after every row, each at most once, in this order:

- `head: Card | Worth`: printed column titles, two cells. Without it the table has no header row.
- `caption: …`: one line drawn under the table, last in the block.

Attributes (`README.md`, "Attributes"):

- `name`: the table's id, unique within its file. Scorekeep requires it, because the app and cheat sheet look tables up by name within the game's page; elsewhere it's optional.
- `class`: a site's styling hint.

## Tokens

Column 1 is space-separated tokens from this set:

| Token | Means | Written |
|---|---|---|
| Rank | A card of that rank | `A` `2`–`10` `J` `Q` `K` |
| Joker | A joker | `Joker` |
| Suit | A suit pip | `♠` `♥` `♦` `♣` |
| Die face | One die showing that face | `d1`–`d6` |
| Run | A range of ranks, drawn rank, dash, rank | `2-10` (low first, ranks only) |
| Topped stack | Three face-down cards with a fourth landing face-up on top: "a fourth of the same rank" | `stack:7♣` (the face-up card's rank and suit) |

Die faces have their own form (`d4`) so they never read as ranks: `4 4 4` is three fours from a deck, `d4 d4 d4` is three dice. Repeating a token draws it again (`d1 d1 d1` is three dice).

**Open:** `d1` reads as dice notation and types easily; `⚀`–`⚅` read as pictures in plain text but are hard to type and tiny in most fonts. Proposed: `d1`–`d6` only. `stack:` is the one token with a prefix; a plainer spelling is welcome.

## Word labels

A column-1 cell with **no** tokens in it is a word label, drawn as text in the token column: `Full house`, `Go`, `Thirty-one`, `Ones–Sixes`. That's how a table mixes cards and named combinations.

A cell that **mixes** tokens and other words (`Q K X`, `d1 d7`) is drawn as a word label and warns, because it's almost always a typo.

## Rows that vary with a house rule

Scorekeep's `@if … @end` may wrap a whole `table` fence to pick between two versions (`README.md`, "Project extensions"); Dice 10,000's score table changes one row with the extra-die rule. Both versions carry the same `name`, since only one survives.

README's `name` rule allows this: a name is unique within its file once a project's conditionals are resolved.

`{key}` values fill before the block is read, so a cell can hold one (`{dice-target}`), as long as the filled line still follows this grammar.

## Lines that don't match

A bad line is skipped with a warning (`README.md`, "Lines that don't match"):

```
WARN  table: skipped "K | 0 | free" (want "tokens | text") in "…/golf-4.md:31:1"
```

These lines warn today:

- Too many cells: `K | 0 | free`
- One cell: `K` (no text), `| 0` (no tokens)
- A run that isn't ranks, or runs downward: `d1-d6`, `10-2`
- A keyword before a row, or one this type doesn't take: `caption: …` then `K | 0`; `note: …`
- A second `head:` or `caption:`
- `head:` without exactly two cells

Recoverable, drawn and warned: a cell mixing tokens and other words (drawn as a word label).

A block with no valid rows shows its source as preformatted text.

Scorekeep's `RulesDocumentTests` fails on any warning and on a `name` the app asks for that the page doesn't define, so a bad table never ships.

## Rendering in Scorekeep

Not part of the spec; for reference when porting.

- **App.** `RulesDocument` (ScorekeepCore) parses the rows; `SpecialCardTable` draws them, each token as a `GlyphCard` (`Scorekeep/Design/PlayfieldTokens.swift`): ranks and jokers as small cards, die faces as pips, suits as pips, a run with a dash between, the topped stack as its little pile. Word labels are chrome type in the same column. The cheat sheet (`CheatSheetView`) shows the same rows collapsed, looked up by `name`. This replaces the Swift row sets (`.golfCardValueRows` and kin) and `@table`.
- **Web.** `render-codeblock-table.html` writes a `<table class="sk-table">` inside the site's `.table-scroll` wrapper, `head:` as a `<thead>`, `caption:` as `<caption>`. Tokens are `<span class="sk-card">`, `sk-die`, `sk-suit`; word labels `sk-label`. Card ranks have their text in the span, so a screen reader reads "K, 0". Classes all start `sk-`.
- **Plain text.** Align the pipes; rows read as "K | 0" in Obsidian and on GitHub.
