# The reminders block

A fenced code block with the info string `reminders` holds table-prep notes: what to do before the first deal, such as how many decks to shuffle and how many jokers to add. It's a **data** fence (`README.md`, "Kinds"), one note per line. Used by Scorekeep, in a game's `docs/rules/<game>.md`; shipped 2026-10-26, the first block Scorekeep wrote as a fence.

## Syntax

````markdown
```reminders
Shuffle {decks} with {jokers} jokers.
Last game's Village Idiot deals.
```
````

Each non-blank line is one note: a **text line** (`README.md`, "Lines"), taken whole, drawn as written. A note is plain text plus `{key}` values; no inline Markdown.

The type takes no keywords and no `name`. A page has at most one `reminders` block. Attribute: `class` only.

`{key}` values fill before the block is read (Scorekeep, `README.md`, "Project extensions"). The keys a note can use are the ones the page's game supplies; for table prep today that's `{decks}` and `{jokers}`, worked out from the player count.

## Lines that don't match

```
WARN  reminders: skipped "caption: Before you deal" (want "a note") in "…/swipe.md:16:1"
```

These lines warn today:

- A keyword line: `caption: …`, `players: 4` (the type takes none, so a lowercase `key: ` start is read as a keyword, not a note; write `Players: …` or reword)
- A Markdown list marker: `- Shuffle two decks.` (a note is the whole line; drop the `- `)
- A second `reminders` block on the same page

A block with no valid lines shows its source as preformatted text.

## Rendering in Scorekeep

Not part of the spec; for reference when porting.

- **App.** Shown at New Game, on the options step, written on the paper in grease pencil with a slight tilt: the note's first number circled the way a pencil marks it, then a pencil underline (`TableReminders`, `Scorekeep/Design/TableReminders.swift`). The counts come from `GameKind.tablePrep(players:)` and follow the roster as it's edited. A game played with one plain deck shows nothing, whatever its page says. VoiceOver reads "Before you deal:" then the notes. Not drawn on the How to play page.
- **Web.** `render-codeblock-reminders.html` draws a "Before you deal" box (`<aside class="sk-reminders">`, one `<p>` per note) where the fence sits on the page, with `{decks}` and `{jokers}` filled for 4 players, the site's default lineup.
