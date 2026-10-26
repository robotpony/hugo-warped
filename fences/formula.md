# The formula block

A fenced code block with the info string `formula` draws a ratio or a method's shape as a row of icons, each with a label, a quantity and optional swaps. It's a **diagram** fence (`README.md`, "Kinds"). Not a Chef owns it and is its only user; w42 shows one as source in its manifesto but doesn't draw it.

The reference hook is Fugu's `layouts/_default/_markup/render-codeblock-formula.html`, with each slot drawn by `layouts/partials/formula-slot.html`.

## Syntax

````markdown
```formula
can          | Beans   | 1 can         | black, pinto, chickpea
+ bowl       | Starch  | 1 cup         | rice, mash, quinoa
+ crumbs egg | Binder  | ½ cup + 1 egg | or gluten + oats
= patty      | Patties | 6
caption: Per can of beans
```
````

One slot per row, `icon | label | quantity | swaps`:

1. **Operator.** A marker at the start of every row after the first, followed by a space: `+` (parts that go together), `:` (a ratio; the quantity is the ratio number), or `→` (the shape of a method; a quantity that isn't a number prints as an italic note). `->` is accepted for `→`. One operator per block. A later row with no marker is joined by the block's operator. An optional last row starting `=` names the result.
2. **Icon.** Tokens: one or two keys from Fugu's `assets/icons/formula/`. An unknown key draws a placeholder and warns.
3. **Label.** Inline text, one short word. Required.
4. **Quantity.** Inline text. Optional.
5. **Swaps.** Optional, up to three, comma-separated.

Keywords, as a trailer after every row, in either order and once each: `caption: <text>`, and `bar: yes` for a ratio's proportion bar.

Keep it to five slots.

## Use

The diagram illustrates the sentence; it MUST NOT replace it. Only draw a ratio the text already states. In a recipe it sits in the `## Mechanic` section, which the recipe sidebar shows.

## Lines that don't match

These warn:

- An unknown icon key: drawn as a placeholder. `unknown-token`
- A second operator kind in one block (`+` then `:`): the row draws with its own marker. `mixed-markers`
- A marker on the first drawn row (`+ can | Beans`), which is the next valid row when the ones before it are skipped: the marker is dropped and the row draws. `stray-marker`
- More than five slots, counting the `=` row: drawn, and warned on the sixth, since they won't fit the sidebar. `over-limit`
- More than two icon keys, or more than three swaps: drawn. `over-limit`
- More than four cells in a row: the first four draw. `too-many-cells`
- A row with no label (`can`, `can |`): skipped. `missing-cell`
- A row after the `=` row, or after a trailer keyword: skipped. `out-of-order`
- A second `caption:` or `bar:`: skipped. `duplicate-keyword`
- A keyword line this type doesn't take (`note: x`): skipped, with one warning. `unknown-keyword`

## Rendering in Not a Chef

Not part of the spec; for reference when porting.

- Classes are `.formula` and `.f-*`. Compact in the recipe sidebar.
- A new icon file doesn't show in a running `/preview` until the server restarts; it keeps the placeholder it cached.
