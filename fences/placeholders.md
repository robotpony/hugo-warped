# The placeholder blocks: diagram, example, sheet, house-rules

Four fenced code block types mark where a drawing goes whose content comes from somewhere else: an app's own code, a screenshot, a data file. They're **placeholder** fences (`README.md`, "Kinds"): attributes say what to draw, and the body is one plain line describing it. Used by Scorekeep, in its `docs/rules/<game>.md` How to play pages; they replace the `@diagram`, `@example`, `@sheet` and `@house-rules` lines.

## Syntax

````markdown
```diagram {draw="table hand"}
The table from above, then your 2×2 hand up close.
```

```example {draw="golf-revealed"}
A hole's four hands turned face-up and totalled, the low one circled.
```

```sheet
The score sheet: names down the side, holes across, a small X box in each cell.
```

```house-rules
This game's house rules, at the values in play.
```
````

The body is exactly one **text line** (`README.md`, "Lines"): plain text, no Markdown. It says what the drawing shows, in words a reader without it can use. That line is what Obsidian and GitHub show, the web's alt text and its fallback box, and the app's VoiceOver label for the drawing. It may hold `{key}` values (Scorekeep fills them first).

Attributes:

| Type | `draw` | Notes |
|---|---|---|
| `diagram` | Optional. One or more plates, in order. Omitted means `table`. | |
| `example` | Required. Exactly one value. | |
| `sheet` | None. | One per game's page. |
| `house-rules` | None. | At most one per page; a page has one exactly when its game has house rules. |

All four take `class`. None takes `name`: nothing looks a placeholder up.

## Draw values

What `draw` can name. Scorekeep's tests check each value is one the app draws for that page's game.

**`diagram`** (plates; several words make a peek carousel in that order, side by side on a wide iPad):

| Value | Draws | Games |
|---|---|---|
| `table` | The whole table from above, sized to the lineup (opened from Settings, a 2–6 player picker). | Every game |
| `hand` | Your own hand up close. | 4-Card Golf, Village Idiot, both Turtles, Cribbage |
| `turn` | One mechanic as an inline figure under the text it explains: Golf's draw-and-swap turn. | 4-Card Golf |

**`example`** (worked examples, inline under their text):

| Value | Draws | Game |
|---|---|---|
| `dice-on-the-board` | A few sheet cells: a struck-through hand, then the circled one that gets on the board. | Dice 10,000 |
| `golf-hole` | A hole's cells: an X on the low hand, a dashed tie mark, an XX. | 4-Card Golf |
| `golf-revealed` | A hole's hands face-up and totalled, the low one circled; follows the player count. | 4-Card Golf |
| `gin-results` | The K, G and U marks beside a hand's points. | Gin Rummy |
| `gin-melds` | Ten cards sorted into melds and deadwood. | Gin Rummy |

## Lines that don't match

```
WARN  example: skipped "and the total is entered" (want one description line) in "…/golf-4.md:44:1"
```

These warn today:

- A second body line (only the first is the description; the rest are skipped)
- An empty body: drawn without a description, and warned, because an empty placeholder reads like a mistake
- `example` with no `draw`, or more than one value
- `draw` on `sheet` or `house-rules` (ignored)
- A `draw` value the target doesn't know (`draw="table feet"`): the known values draw, the unknown one is skipped. In Scorekeep's app it's a test failure.

## Rendering in Scorekeep

Not part of the spec; for reference when porting.

- **App.** `RulesView` draws each in SwiftUI: `diagram` through `PlayfieldViews` (plates from `RulesPlate`), `example` through its `RulesExample` view, `sheet` as the game's sheet mockup sized to the real lineup, `house-rules` as `HouseRulesList` from `GameOptions.houseRules(for:)`, each led by an `[H]` mark at the value in play (or the Settings default with no game open). The description line becomes the drawing's VoiceOver label.
- **Web.** One hook per type. `diagram`, `example` and `sheet` show a light and dark screenshot pair, `<picture>` swapped on `prefers-color-scheme`, from `site/assets/shots/<game>-<draw>-light.png` and `-dark.png` (`<game>-sheet-…` for a sheet), captured by `tools/screenshots.sh` with the app's DEBUG `-plate` flags; the description is the `alt`. With no shot, a dashed box (`.sk-placeholder`) holding the description and "In the app". `house-rules` draws the `[H]` list from `site/data/rules.json` at the Settings defaults, then "Scorekeep's defaults. Pick different ones at New Game, or set your own under Settings › Games."
- **Not fences.** `@aliases` and `@goal` go away: the app places a game's "also called" line and goal itself, and the site reads them from `games.yaml`. Maxi Dice's `@bullets maxi-joker-rule` becomes two plain bullets in `@if` branches.
