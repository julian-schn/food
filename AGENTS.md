# Recipe repo: agent rules

## Layout
- `recipes/<id>.yaml` one recipe per file, filename == `id` (kebab-case)
- `tags.yaml` controlled tag vocabulary
- `schema/recipe.schema.json` the contract
- `index.json` generated, never edit by hand
- `site/` templates and static assets for the GitHub Pages site. `scripts/build_site.py`
  renders it into `_site/` (generated, never committed; CI builds and deploys it on push to `main`)
- `site/static/art/<id>.png` optional recipe artwork; style, sizes and prompts in `site/static/art/BRIEF.md`

## Adding a recipe
1. Metric only. Convert imperial (lb, oz, cups, °F) before writing.
2. Stovetop heat goes in `heat` on the 1-9 scale. Oven gets `oven.temp_c` + `oven.mode`
   (default `ober-unter`; convert umluft/ober-unter explicitly, don't guess).
3. Every ingredient gets a short snake_case `id`. Reference it in step text as `{id}`.
4. Every recipe is bilingual. All prose fields (title, description, notes, ingredient
   name/substitute/group, step title/text) are `{de: ..., en: ...}`, both required.
   `source_lang` is the language it came in. That version is authoritative; if the two
   ever disagree, fix the translation, not the original.
   - Ingredient names: use what you'd find in a German shop for `de` (Schmorbraten,
     Butterschmalz, Speisestärke), and the natural English name for `en`. Keep a German
     term in parentheses in `en` when there's no clean equivalent (Rübensirup).
   - Every `{ingredient_id}` must appear in both languages of a step. The validator checks.
   - Don't translate `log` notes, `source.credit` or tag values.
5. `source.url` for web recipes. `type: adapted` if we changed anything meaningful.
6. Tags: only values from `tags.yaml`. Map through `aliases` first.
   If nothing fits, add an entry to `proposed` with a reason and leave the tag off.
   Never add derived tags (`time:*`, `tried`, `favourite`), the script computes those.

## Editing
- Never delete or rewrite `log` entries. Append only.
- Edits to prose update both languages in the same commit.
- Adaptations the user settles on (e.g. "Keule ohne Knochen, 2.5h") update the recipe
  itself; the reason goes in `notes`.
- A genuinely different version of a dish is a new file, not a mutation.

## Before every commit
Run `.venv/bin/python scripts/build_index.py`. It must pass, and `index.json` is committed with the change.
First-time setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

## Commits
Conventional commits, one recipe per commit:
- `feat(recipe): add lammkeule geschmort`
- `fix(recipe): correct oven temp in pot-roast`
- `chore(log): cooked buldak-carbonara`
- `chore(tags): add cuisine:vietnamese`
