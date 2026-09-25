# Artwork brief

Line-art images for the recipe site. Every recipe shows one in its header and as a strip on
its index card. Recipes without their own image get one of the generic fallbacks. The site
works without any of them; art only adds to it.

## Style

- Monochrome **scientific / botanical diagram** line art.
- Thin strokes of **uniform weight**. **Every line ends in a small filled dot**, like dandelion
  seed heads.
- Motifs are built from **radiating starbursts**: stems, roots, veins and gills fan out
  from centres.
- Forbidden: fills, shading, hatching, gradients, texture, paper grain, text, lettering,
  numbers, borders, frames, signatures, watermarks, people, hands, plates, bowls, cutlery,
  tables, photorealism, 3D.

## Colour

Exactly two colours, no anti-aliasing tint toward anything else:

| role | hex |
|---|---|
| lines and dots | `#1C1C1A` |
| background (flat, solid) | `#D6D3C8` |

The background matches the site's paper colour, so the image blends into its panel.
**No red, no blue**: the site adds the red rules and the blue pixel mark itself.

## Composition

- Dense clusters that **bleed off at least two edges**.
- The key subject sits in the **central horizontal band** (the middle third of the height), because
  index cards crop recipe images to a 3:1 strip around the centre.
- About **30 % empty background**, not evenly scattered.
- No single centred "icon" composition.

## Files

| file | size (px) | ratio | motif |
|---|---|---|---|
| `buldak-carbonara.png` | 1800×1200 | 3:2 | dried chili peppers, and burst lines of chili seeds |
| `chicken-gnocchi-walnuts.png` | 1800×1200 | 3:2 | walnut halves with the vein pattern drawn as radiating lines, sage leaves |
| `geschmorte-lammschulter.png` | 1800×1200 | 3:2 | rosemary sprigs radiating like a starburst, whole garlic bulb with root threads |
| `haehnchengeschnetzeltes-mit-pilzen.png` | 1800×1200 | 3:2 | mushrooms seen from below, gills as radiating dot-ended lines |
| `loaded-potato-soup.png` | 1800×1200 | 3:2 | potato with sprouting eyes as bursts, a bundle of chives fanning out |
| `pot-roast-roemertopf.png` | 1800×1200 | 3:2 | carrot tops fanning out, bay leaves, peppercorn bursts |
| `_index.png` | 2400×800 | 3:1 | a field of dill umbels (natural starbursts) at different scales |
| `_social.png` | 1200×630 | ~1.9:1 | a single large dill umbel, off-centre left (link previews) |
| `_fallback-1.png` | 1800×1200 | 3:2 | peppercorn and star anise bursts |
| `_fallback-2.png` | 1800×1200 | 3:2 | onion with root threads |
| `_fallback-3.png` | 1800×1200 | 3:2 | parsley umbels |

11 images in total. PNG, sRGB. `.webp` and `.jpg` also work; the build picks whichever exists,
in the order webp, png, jpg.

## Prompt template

```
Monochrome scientific line illustration of {motif}. Thin uniform ink strokes, every line
ending in a small filled dot, radiating starburst structures like dandelion seed heads,
botanical diagram style. Ink #1C1C1A on flat solid background #D6D3C8. No shading, no fill,
no texture, no text, no frame, no colour. {W}x{H}, subject cropped and bleeding off the
edges, key detail in the central horizontal band.
```

## Adding art for a new recipe

1. Generate it with the template above, 1800×1200, motif = the dish's defining ingredient.
2. Save it as `site/static/art/<recipe-id>.png` (the id is the YAML filename).
3. Rebuild with `.venv/bin/python scripts/build_site.py`, then check the recipe page and its index card.

Keep each file under about 250 KB. Convert with `cwebp -q 80 in.png -o out.webp` if one is larger.
