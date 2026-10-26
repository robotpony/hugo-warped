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

1. **Layer.** A token: a key from Fugu's `assets/icons/layers/` (the full list is in Fugu's `docs/recipe-format.md`, "Stack diagrams"). An unknown key draws a dashed placeholder and warns. Pick the layer that matches the label: `lettuce` is a single leaf, `lettuce-shredded` a heap of shreds. Patties are griddled unless the key says `-grilled`.
2. **Label.** Inline text: what the layer is, with the pick's quantity when there is one.
3. **Role.** Inline text: what it does for the whole. Optional.

Keywords, as a trailer:

- `caption: <text>`.
- `repeat: <from>-<to> x<n>` marks layers as repeated: `repeat: 3-5 x3` draws a `× 3` bracket beside layers 3 to 5. `×` works for `x`, a single layer works (`repeat: 4 x2`), and a block can have several `repeat:` lines.

## Use

On a build page the first `stack` block goes under `## Picks`, and its layers MUST follow the picks (`docs/FORMAT.md`, "Blueprints"). A build that isn't layered has no `stack` block.

## Lines that don't match

These warn:

- An unknown layer key: drawn as a dashed placeholder.
- A `repeat:` line that doesn't read (`want repeat: 3-5 x3`).
- A `repeat:` range outside the block's layers.

## Rendering in Not a Chef

Not part of the spec; for reference when porting.

- A small unlabelled copy goes on the build's card on its blueprint page.
- Layer drawings come from `mockups/exploded-builds.html`, exported with `mockups/export-layers.mjs`.
