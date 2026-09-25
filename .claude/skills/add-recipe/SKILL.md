---
name: add-recipe
description: Ingest a new recipe into this repo from a URL, a photo or screenshot, or pasted text, and turn it into a validated, bilingual recipes/<id>.yaml with its own commit. Use when asked to add, import, save or ingest a recipe, or when handed a recipe link or picture.
---

# Add a recipe

The rules live in `AGENTS.md` ("Adding a recipe", "Before every commit", "Commits").
This skill is the order to apply them in. Where the two disagree, `AGENTS.md` wins.

## 1. Read the input
- **URL:** fetch the page and pull out the recipe card: ingredients, steps, times, servings.
  Skip the story around it. Keep the URL for `source.url`.
- **Photo / screenshot:** transcribe it. Where a word or number is unreadable, ask; don't guess.
- **Pasted text:** use as is.

Set `source_lang` to the language the recipe came in. That version is authoritative.
Set `source.type`: `web` for a URL used unchanged, `adapted` if anything meaningful changes,
`person` if someone gave it to you, `original` if it's the user's own.

## 2. Check for duplicates
```
grep -il '<main ingredient>\|<dish name>' recipes/*.yaml
```
Close match? Ask whether this is a different version (new file) or a change to the existing one
(edit it, reason in `notes`). Don't decide alone.

## 3. Draft `recipes/<id>.yaml`
- `id`: kebab-case, ASCII (`ä` → `ae`), filename == id.
- Copy the structure of the most similar existing recipe (stovetop:
  `haehnchengeschnetzeltes-mit-pilzen.yaml`, oven/braise: `pot-roast-roemertopf.yaml`).
  `schema/recipe.schema.json` is the full contract.
- Apply AGENTS.md "Adding a recipe" 1–6: metric, `heat` 1–9 / `oven.temp_c` + `oven.mode`,
  snake_case ingredient ids referenced as `{id}` in both languages, every prose field `{de, en}`,
  tags only from `tags.yaml` (via `aliases`; otherwise add a `proposed` entry and leave the tag off).
- Never set `time:*`, `tried`, `favourite`. No `log` entry unless the user says they cooked it.

## 4. Ask only about real gaps
Ask once, all together, about things the source doesn't say and a wrong guess would ruin:
oven mode (umluft vs ober-unter), servings, whether an ingredient is optional.
Everything you converted or estimated goes in `notes`, in both languages
(e.g. "Original in cups, umgerechnet"). Write `notes` as a `>-` block and separate topics
(conversions / tips / storage) with a blank line; the site renders each as its own paragraph.

## 5. Validate and look at it
```
.venv/bin/python scripts/build_index.py
.venv/bin/python scripts/build_site.py
```
Both must pass. If the local server isn't running:
`tmux new -d -s food-site '.venv/bin/python -m http.server -d _site 8000'`,
then open `http://localhost:8000/r/<id>/` and check that the `{id}` refs read naturally in both languages.

## 6. Commit
One recipe per commit: `recipes/<id>.yaml` + `index.json` (+ `tags.yaml` if you added to `proposed`).
```
feat(recipe): add <name as the user would say it>
```
