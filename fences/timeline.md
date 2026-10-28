# The timeline block

A fenced code block with the info string `timeline` draws dated entries as dots on a track of decades. It's a **diagram** fence (`README.md`, "Kinds"), shared by warpedvisions.org (the w42 theme) and bruce-loves-to-cook.ca (the Fugu theme), and specified here since 2026-10-26 (it began in w42's `themes/w42/docs/`). Each site keeps its own hook and CSS; the syntax below is what both accept.

The reference hook is w42's `layouts/_default/_markup/render-codeblock-timeline.html`. It hands the block to `layouts/partials/diagrams/timeline.html`, which draws it (CSS in `assets/css/common/timeline.css`), by way of `layouts/partials/diagram.html`, which adds an (i) toggle to the fenced source. The toggle is w42's, not part of the spec.

## Syntax

````markdown
```timeline
1983 Atari BASIC
1994 *The UNIX Philosophy*
1996 Carmack's `.plan` files
2002 [Blosxom](https://blosxom.sourceforge.net/)
~2008 WordPress, a detour
2022 Hugo
```
````

One entry per line:

1. **Year.** Four digits at the start of the line (`1983`).
2. **Faint marker.** An optional `~` right before the year (`~2008`) marks the entry as faint: a detour, a tentative start, or a draft. It doesn't mean "circa".
3. **Separator.** One or more spaces or tabs after the year.
4. **Label.** The rest of the line, as written: brackets, pipes, backticks and all. Nothing in it is parsed by the hook, except a `←` note at the end, which is dropped (`README.md`, "Notes").

Leading and trailing whitespace on a line is ignored, and blank lines are skipped. As a pattern: `^(~?)(\d{4})\s+(.+)$`.

## Labels

A label is inline Markdown, rendered with the page's own `RenderString` and `"display" "inline"`, so each site's render hooks apply (links, images, code). A label that's a link makes its entry a link; there's no other syntax for linked entries.

Sites that rewrite their own syntax before Goldmark runs keep it. For example, the cookbook turns `[[Whopper]]` into `[Whopper](<Whopper>)` in Fugu's `layouts/_default/single.html`, so the hook sees and renders a normal link.

## Order

Entries are drawn in year order, whatever order the lines are in. Lines with the same year keep their line order. The output is an ordered list (`<ol>`) in that order.

## The track

The track runs from the first year's decade (1983 → 1980) to the last year rounded up to a decade (2022 → 2030). When every year sits on one decade boundary, the track runs one decade past it. How the track, ticks and labels are drawn is up to each site; w42's choices are under "Rendering in w42".

## Clusters

*Approved 2026-10-27, at Bruce's request, for the timeline fence and for any drawing of dated dots on a track, such as Not a Chef's lineage. It changes no syntax: the block's text reads as before, and only a crowded track draws differently.*

Years close together crowd their dots into one blob: 1988, 1989 and 1991 on a decade track. A site SHOULD zoom the track slightly where that happens, so each dot can be read on its own.

1. **Gap.** Each site sets a minimum gap between two dots, enough that they don't touch, and records it under its "Rendering" section. The zoom spaces dots, not labels: labels keep the site's own placement (rows, leaders). A gap of one label row also clears the labels; a smaller one may leave long labels crowding inside the zoom.
2. **Cluster.** Take the distinct years in order. Two neighbours closer on the scale than the gap belong to one cluster, and a run of such neighbours is one cluster. Entries sharing a year share a dot, so they never make a cluster on their own.
3. **Zoom.** A cluster's span gets just the length it needs to put each pair of its neighbours one gap apart. The rest of the track keeps its own scale, shrunk only as much as the column needs to make room. Nothing else is re-scaled. A track with no cluster draws exactly as before.
4. **Mark it.** A zoomed span is drawn so a reader can see the scale changed: small break marks at each end, or a slightly different track. Inside it, each year gets a short tick (`'88`, `'89`, `'91`) in place of the decade ticks it covers.
5. **Narrow screens.** Where the track turns into a list (w42 under 640px), there's nothing to zoom.

The zoom is the site's: the parse (`year`, in source order) doesn't change, and no fixture covers a drawing.

## Lines that don't match

A line that doesn't match the syntax isn't drawn. The hook prints a build warning that quotes the line and gives its file and line number:

```
WARN  timeline: skipped "1950s Decade entry" (want "YEAR Label") in "…/index.md:21:1"
```

These lines warn today:

- No label: `1983` `missing-label`
- Not four digits: `83 Atari BASIC`, `19830 Atari BASIC` `bad-year`
- A decade: `1950s Label` `bad-year`
- A range: `1955-1960 Label` `bad-year`
- A month or day: `1983-04 Label` `bad-year`
- Anything before the year other than `~`: `- 1983 Atari BASIC`, `c. 1983 Atari BASIC` `bad-year`
- A keyword line (`caption: …`): the type takes none `unknown-keyword`

A warning means "not drawn yet", not "never valid".

A block with no valid lines shows its source as preformatted text, as for every type (`README.md`, "Lines that don't match").

## Room to grow

Decade entries (`1950s Label`) and ranges (`1955-1960 Label`, `~1955-1960 Label`) are reserved, but not yet specified or drawn. Any extension:

- must be agreed between both sites and written here first;
- must leave every line that's valid today drawing the same way;
- must keep the label as "the rest of the line after the first run of whitespace following the date".

## Rendering in w42

Not part of the spec; for reference when porting.

- Classes all start with `tline` (`.tline`, `.tline-track`, `.tline-list`, `.tline-mark`, `.tline-dot`, `.tline-name`, `.tline-year`, `.tline-ticks`, `.tline-tick`), so they don't collide with the cookbook's lineage (`.timeline`, `.tl-*`). The hook writes classes and inline position variables only (`left`, `--row`, `--up`, `--down`); colours come from each theme's CSS.
- A tick crosses the track at each decade, with its year centred just under it. Tracks over 80 years name every other decade. The track is inset 16px at each side so the end years fit inside the column.
- Labels alternate above and below the track by entry order. A label that would go below, but whose leader would cross a decade's year, goes above instead, and the next one goes below. On each side, a label takes the nearest row its estimated width clears. Every label has a leader to its dot.
- Labels near either end align to their dot's side so they stay on the track.
- Faint entries have a hollow dot and a muted label.
- At 640px and below, the track becomes a vertical list with each year after its label.
