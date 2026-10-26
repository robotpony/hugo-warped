# The stack block

A fenced code block with the info string `stack` draws a build made of layers (a burger, a sandwich, a lasagne) as an exploded view, top first. It's a **diagram** fence (`README.md`, "Kinds"). Not a Chef owns it and is its only user.

The reference hook is Fugu's `layouts/_default/_markup/render-codeblock-stack.html`, which draws through `layouts/partials/stack/draw.html`.

## Syntax

````markdown
```stack
bun-top          | Toasted bun       | soft, toasted
lettuce-shredded | Shredded lettuce  | cold crunch
patty-thin       | Thin patty, 140 g | salt, fat, savoury
bun-base         | Toasted bun       | barrier
caption: Drive-in deluxe
```
````

One layer per row, top first, `layer | label | role`:

1. **Layer.** A token: a key from Fugu's `assets/icons/layers/` (the full list is in Fugu's `docs/recipe-format.md`, "Stack diagrams"). An unknown key draws a dashed placeholder and warns. Pick the layer that matches the label: `lettuce` is a single leaf, `lettuce-shredded` a heap of shreds. Patties are griddled unless the key says `-grilled`. A spread on its bun is one layer, written as a pair, `bun-base + mayo` (the spaces are optional); it draws the pair's own drawing, not two layers. A pair the theme has no drawing for is an unknown key.
2. **Label.** Inline text: what the layer is, with the pick's quantity when there is one. Required.
3. **Role.** Inline text: what it does for the whole. Optional.

Keywords, as a trailer after every row, in either order:

- `caption: <text>`, once.
- `repeat: <from>-<to> x<n>` marks layers as repeated: `repeat: 3-5 x3` draws a `× 3` bracket beside layers 3 to 5. `×` works for `x`, a single layer works (`repeat: 4 x2`), and a block can have several `repeat:` lines, which may overlap or nest. The count is a whole number, 2 or more.

## Use

On a build page the first `stack` block goes under `## Picks`, and its layers MUST follow the picks (Not a Chef's `docs/FORMAT.md`, "Blueprints"). A build that isn't layered has no `stack` block.

## Lines that don't match

These warn:

- An unknown layer key or pair: drawn as a dashed placeholder. `unknown-token`
- A `repeat:` line that doesn't read (`want repeat: 3-5 x3`), or a count that isn't a whole number of 2 or more (`x two`, `x1`): skipped. `bad-repeat`
- A `repeat:` range that runs backwards (`5-3`) or outside the block's layers: skipped, and reported on the `repeat:` line. `bad-repeat`
- More than three cells in a row: the first three draw. `too-many-cells`
- A row with no label (`bun-top`, `bun-top |`): skipped. `missing-cell`
- A row after a trailer keyword: skipped. `out-of-order`
- A second `caption:`: skipped. `duplicate-keyword`
- A keyword line this type doesn't take (`note: x`): skipped, with one warning. `unknown-keyword`

## Rendering in Not a Chef

Not part of the spec; for reference when porting.

- A small unlabelled copy goes on the build's card on its blueprint page.
- Layer drawings come from Not a Chef's `mockups/exploded-builds.html`, exported with `mockups/export-layers.mjs`.
