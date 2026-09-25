"""Render the recipe collection as a static site into _site/.

Usage: python scripts/build_site.py
Set GITHUB_REPOSITORY (owner/repo, set automatically in Actions) to get
"view source" links on recipe pages.
"""
import json, os, re, shutil, sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_index import ROOT, REF, load_recipes, flat_tags, vocab  # noqa: E402

OUT = ROOT / "_site"
SITE = ROOT / "site"
REPO = os.environ.get("GITHUB_REPOSITORY")

FACETS = {
    "course": {"de": "Gang", "en": "Course"},
    "cuisine": {"de": "Küche", "en": "Cuisine"},
    "protein": {"de": "Protein", "en": "Protein"},
    "method": {"de": "Methode", "en": "Method"},
    "equipment": {"de": "Geräte", "en": "Equipment"},
    "effort": {"de": "Aufwand", "en": "Effort"},
    "season": {"de": "Saison", "en": "Season"},
    "mood": {"de": "Stimmung", "en": "Mood"},
    "time": {"de": "Zeit", "en": "Time"},
    "status": {"de": "Status", "en": "Status"},
}
DERIVED = {"time": ["time:quick", "time:weeknight", "time:slow"], "status": ["tried", "favourite"]}
UNITS = {
    "g": ("g", "g"), "kg": ("kg", "kg"), "ml": ("ml", "ml"), "l": ("l", "l"),
    "tsp": ("TL", "tsp"), "tbsp": ("EL", "tbsp"), "pinch": ("Prise", "pinch"),
    "piece": ("", ""), "to-taste": ("nach Geschmack", "to taste"), None: ("", ""),
}
OVEN = {"ober-unter": ("Ober-/Unterhitze", "conventional"), "umluft": ("Umluft", "fan"),
        "grill": ("Grill", "grill"), None: ("", "")}


def fmt_amount(x, lang: str) -> str:
    if x is None:
        return ""
    s = f"{x:g}" if isinstance(x, float) else str(x)
    return s.replace(".", ",") if lang == "de" else s


def fmt_minutes(m: int) -> str:
    h, m = divmod(m, 60)
    return f"{h} h {m} min" if h and m else f"{h} h" if h else f"{m} min"


def fmt_timer(sec: int) -> str:
    h, rest = divmod(sec, 3600)
    m, s = divmod(rest, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


def refs(text: str, ings: dict, lang: str) -> Markup:
    """Escape step text and turn {ingredient_id} into a linked ingredient name."""
    def sub(m):
        i = ings[m.group(1)]
        full = i["name"][lang]
        # "Rinderbraten (Zungenstück…)" → "Rinderbraten", but keep lists like "Muskat, Salz, Pfeffer"
        parts = full.split(", ")
        is_list = len(parts) >= 3 and all(" " not in p for p in parts)
        short = full if is_list else re.split(r" \(|, ", full, maxsplit=1)[0]
        return (f'<span class="ing" data-ing="{i["id"]}" title="{escape(full)}">'
                f'{escape(short)}</span>')
    return Markup(REF.sub(sub, str(escape(text))))


# "55 g", "3-5 Minuten", "20 %": a line break between number and unit reads badly.
UNIT_WORDS = (r"g|kg|ml|l|cm|mm|h|min|Min\.?|Minuten|Stunden?|minutes?|hours?|Sekunden|seconds?"
              r"|°C|%|EL|TL|tbsp|tsp|Prisen?|pinch|cups?|lb|oz|Stück|pieces?|Scheiben|slices?")
NUM_UNIT = re.compile(rf"(\d) (?=(?:{UNIT_WORDS})(?![\w]))")


def keep_units(value):
    """Jinja finalize: glue numbers to their units with a no-break space in all rendered text."""
    if isinstance(value, str):  # Markup is a str subclass and stays Markup
        return value.__class__(NUM_UNIT.sub("\\1\u00a0", value))
    return value


def tag_label(tag: str) -> str:
    return tag.split(":", 1)[-1]


def build():
    recipes, failed = load_recipes()
    if failed:
        return 1
    env = Environment(loader=FileSystemLoader(SITE / "templates"),
                      autoescape=select_autoescape(), trim_blocks=True, lstrip_blocks=True,
                      finalize=keep_units)
    env.filters.update(amount=fmt_amount, minutes=fmt_minutes, timer=fmt_timer,
                       refs=refs, tag_label=tag_label)
    env.globals.update(UNITS=UNITS, OVEN=OVEN, FACETS=FACETS)

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SITE / "static", OUT / "static")
    (OUT / ".nojekyll").touch()

    cards = []
    for path, r in recipes:
        tags = flat_tags(r)
        r["_tags"] = tags
        r["_ings"] = {i["id"]: i for i in r["ingredients"]}
        r["_groups"] = []  # consecutive ingredients sharing a group, in file order
        for i in r["ingredients"]:
            if not r["_groups"] or r["_groups"][-1][0] != i.get("group"):
                r["_groups"].append((i.get("group"), []))
            r["_groups"][-1][1].append(i)
        r["_source_url"] = f"https://github.com/{REPO}/blob/main/recipes/{path.name}" if REPO else None
        ratings = [e["rating"] for e in r.get("log", []) if "rating" in e]
        r["_rating"] = round(sum(ratings) / len(ratings), 1) if ratings else None
        cards.append({
            "id": r["id"], "title": r["title"], "description": r.get("description"),
            "time_total": r["time"]["active"] + r["time"]["passive"], "tags": tags,
            "rating": r["_rating"],
        })
        page = OUT / "r" / r["id"] / "index.html"
        page.parent.mkdir(parents=True)
        page.write_text(env.get_template("recipe.html").render(r=r, root="../../"))

    used = {t for c in cards for t in c["tags"]}
    facets = [(f, [f"{f}:{v}" for v in spec["values"] if f"{f}:{v}" in used])
              for f, spec in vocab.items()]
    facets += [(f, [t for t in ts if t in used]) for f, ts in DERIVED.items()]
    facets = [(f, ts) for f, ts in facets if ts]
    (OUT / "index.html").write_text(env.get_template("index.html").render(
        cards=cards, facets=facets, root="",
        data=Markup(json.dumps([{k: c[k] for k in ("id", "title", "description", "tags")}
                                for c in cards], ensure_ascii=False).replace("</", "<\\/"))))
    print(f"✓ site: {len(cards)} recipes → {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(build())
