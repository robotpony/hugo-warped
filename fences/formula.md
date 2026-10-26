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

1. **Operator.** A marker at the start of every row after the first: `+` (parts that go together), `:` (a ratio; the quantity is the ratio number), or `→` (the shape of a method; a quantity that isn't a number prints as an italic note). `->` is accepted for `→`. One operator per block. An optional last row starting `=` names the result.
2. **Icon.** Tokens: one or two keys from Fugu's `assets/icons/formula/`. An unknown key draws a placeholder and warns.
3. **Label.** Inline text, one short word.
4. **Quantity.** Inline text. Optional.
5. **Swaps.** Optional, up to three, comma-separated.

Keywords, as a trailer: `caption: <text>`, and `bar: yes` for a ratio's proportion bar.

Keep it to five slots.

## Use

The diagram illustrates the sentence; it MUST NOT replace it. Only draw a ratio the text already states. In a recipe it sits in the `## Mechanic` section, which the recipe sidebar shows.

## Lines that don't match

These warn:

- An unknown icon key: drawn as a placeholder.
- A second operator kind in one block (`+` then `:`).
- More than five slots: drawn, since they won't fit the sidebar.

**Gap:** the hook ignores a fifth cell and later ones rather than warning, as the shared grammar asks. It changes to match when the validator lands.

## Rendering in Not a Chef

Not part of the spec; for reference when porting.

- Classes are `.formula` and `.f-*`. Compact in the recipe sidebar.
- A new icon file doesn't show in a running `/preview` until the server restarts; it keeps the placeholder it cached.
