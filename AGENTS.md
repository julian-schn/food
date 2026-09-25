# Recipe repo: agent rules

## Layout
- `recipes/<id>.yaml` one recipe per file, filename == `id` (kebab-case)
- `tags.yaml` controlled tag vocabulary
- `schema/recipe.schema.json` the contract
- `index.json` generated, never edit by hand

## Adding a recipe
1. Metric only. Convert imperial (lb, oz, cups, °F) before writing.
2. Stovetop heat goes in `heat` on the 1-9 scale. Oven gets `oven.temp_c` + `oven.mode`
   (default `ober-unter`; convert umluft/ober-unter explicitly, don't guess).
3. Every ingredient gets a short snake_case `id`. Reference it in step text as `{id}`.
4. `lang` is the language the recipe is written in. Don't translate unless asked.
5. `source.url` for web recipes. `type: adapted` if we changed anything meaningful.
6. Tags: only values from `tags.yaml`. Map through `aliases` first.
   If nothing fits, add an entry to `proposed` with a reason and leave the tag off.
   Never add derived tags (`time:*`, `tried`, `favourite`), the script computes those.

## Editing
- Never delete or rewrite `log` entries. Append only.
- Adaptations the user settles on (e.g. "Keule ohne Knochen, 2.5h") update the recipe
  itself; the reason goes in `notes`.
- A genuinely different version of a dish is a new file, not a mutation.

## Before every commit
Run `python scripts/build_index.py`. It must pass, and `index.json` is committed with the change.

## Commits
Conventional commits, one recipe per commit:
- `feat(recipe): add lammkeule geschmort`
- `fix(recipe): correct oven temp in pot-roast`
- `chore(log): cooked buldak-carbonara`
- `chore(tags): add cuisine:vietnamese`
