# Fence fixtures

Sample blocks with their expected parse, the source of truth for every parser of the spec: the validator, the Hugo partials, and Scorekeep's `RulesDocument`. When a parser and a fixture disagree, the fixture wins, unless the spec says otherwise; then the fixture is the bug.

## Layout

- `<type>/<case>.md`: one whole fence, opening and closing lines included, starting on line 1.
- `<type>/<case>.json`: what a parser reads from it.
- `page/<case>.md` and `.json`: whole pages, for the checks that need more than one block (`duplicate-name`, `duplicate-block`, `unclosed-fence`) and for ordinary code blocks, which never warn.
- `VERSION`: the date and the spec commit these fixtures match. A project that vendors a copy compares it to tell when the copy is stale.

Every type has fixtures.

## Expected output

````json
{
  "type": "table",
  "kind": "data",
  "attributes": {"name": "card-values"},
  "lines": [
    {"line": 2, "row": ["K", "0"], "marker": null, "tokens": [{"rank": "K"}]},
    {"line": 3, "keyword": "caption", "value": "Kings are free."}
  ],
  "warnings": [{"line": 4, "code": "too-many-cells"}],
  "fallback": false
}
````

- **`line`** counts from the opening fence as line 1. In `page/` fixtures it's the file's line.
- **`attributes`** are the `{…}` group as written, every value a string. Unknown keys are kept and never warn. A group that doesn't parse is dropped whole (`{}`, plus `bad-attributes`).
- **`lines`** are the lines a parser keeps, in order, with notes stripped, cells trimmed and `\←` read as `←`. Skipped, blank and note-only lines are left out. Each is one of:
  - a row: `row` (the cells), `marker` (or `null`), and typed column 1 where the type defines it;
  - a keyword line: `keyword` and `value`, plus `cells` for `head:`;
  - a text line: `text`.
- **`warnings`** are compared by `line` and `code` only, in any order. Messages are each parser's own.
- **`fallback`** is `true` when nothing in the block can be drawn and its source shows instead. `lines` still lists anything that parsed, such as a caption with no rows.
- **`page/` fixtures** hold only `warnings`: every warning in the file, from its blocks and the page.

### Typed cells

`table` column 1 is either `tokens` or `label`:

| Token | Written | Expected |
|---|---|---|
| Rank | `K`, `10` | `{"rank": "K"}` |
| Joker | `Joker` | `{"joker": true}` |
| Suit | `♣` | `{"suit": "♣"}` |
| Die face | `d4` | `{"die": 4}` |
| Run | `2-10` | `{"run": ["2", "10"]}` |
| Topped stack | `stack:7♣` | `{"stack": {"rank": "7", "suit": "♣"}}` |
| Word label | `Full house` | `"label": "Full house"` in place of `tokens` |

`formula` rows add `icons` (column 1's keys, in order, unknown ones included) and `swaps` (column 4 split on commas and trimmed, `[]` when there's none). Their `marker` is `+`, `:`, `→` or `=`, with `->` read as `→`, and `null` on the first row and on a later row written without one.

`stack` rows add `layer`: column 1 with the spaces around a pair's `+` removed (`bun-base + mayo` is `"bun-base+mayo"`), unknown keys included. Its `marker` is always `null`. A `repeat:` line adds `from`, `to` and `times` as numbers; `repeat: 4 ×2` is `4`, `4`, `2`.

`timeline` entries are `marker` (`~` or `null`), `year` as a number, and `label` as written, in source order; drawing them in year order is the hook's job.

`flow` steps are rows of one or two cells, with `marker` `→` (`->` read as `→`) or `null`, and `null` where a stray arrow was dropped. A `row:` line is a keyword line, `value` `""` when it has no label. A `row:` with no steps isn't drawn, so it's left out of `lines`.

`tabs` panels are keyword lines, `tab`, whose `value` is the label with its note dropped, or `"Tab"` when it has none. Each adds `body`: the lines up to the next `tab:` outside a nested fence, joined with `\n` and with blank lines at either end dropped. The rest of a body is as written, indentation and `←` included.

Placeholders add `draw` (the resolved list: `diagram` with none is `["table"]`, `sheet` and `house-rules` are `null`) and `description` (the text line, or `null` when the body is empty).

## Left out

- **Project extensions.** `@if` and `{key}` filling are Scorekeep's, tested in its own suite. One case each (`table/value-passthrough`, `house-rules/value-passthrough`) checks that an unfilled `{key}` passes through untouched.
- **Icon and layer keys.** `formula`'s set is Fugu's `assets/icons/formula/` and `stack`'s is `assets/icons/layers/`. The fixtures use keys from them, plus `wok`, `bun-brioche` and the pair `bun-base+ketchup` as unknown ones.
- **Target-judged checks.** `unknown-draw` depends on what a target draws for a page's game, and `unknown-type` on a project's own list of types, so neither has a shared fixture.
