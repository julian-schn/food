"""Validate every recipe and regenerate index.json.

Usage: python scripts/build_index.py [--check]
--check fails if index.json is out of date (for CI).
"""
import json, re, sys
from datetime import date
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
schema = Draft202012Validator(json.loads((ROOT / "schema/recipe.schema.json").read_text()))
vocab = yaml.safe_load((ROOT / "tags.yaml").read_text())["facets"]
REF = re.compile(r"\{([a-z0-9_]+)\}")


def validate(path: Path, r: dict) -> list[str]:
    errs = [f"schema: {e.message}" for e in schema.iter_errors(r)]
    if errs:
        return errs
    if r["id"] != path.stem:
        errs.append(f"id '{r['id']}' must match filename '{path.stem}'")
    ids = [i["id"] for i in r["ingredients"]]
    if len(ids) != len(set(ids)):
        errs.append("duplicate ingredient ids")
    for s in r["steps"]:
        name = s["title"]["en"]
        refs = {lang: set(REF.findall(txt)) for lang, txt in s["text"].items()}
        for ref in refs["de"] | refs["en"]:
            if ref not in ids:
                errs.append(f"step '{name}' references unknown ingredient {{{ref}}}")
        if refs["de"] != refs["en"]:
            errs.append(f"step '{name}': de/en reference different ingredients "
                        f"(only de: {sorted(refs['de'] - refs['en'])}, only en: {sorted(refs['en'] - refs['de'])})")
    for facet, val in r["tags"].items():
        if facet not in vocab:
            errs.append(f"unknown tag facet '{facet}'")
            continue
        if not vocab[facet].get("multi", True) and isinstance(val, list):
            errs.append(f"facet '{facet}' takes a single value")
        for v in (val if isinstance(val, list) else [val]):
            if v not in vocab[facet]["values"]:
                errs.append(f"tag {facet}:{v} not in tags.yaml (add it to `proposed` first)")
    return errs


def derived(r: dict) -> list[str]:
    total = r["time"]["active"] + r["time"]["passive"]
    out = []
    if total <= 30: out.append("time:quick")
    elif total <= 60: out.append("time:weeknight")
    elif total > 180: out.append("time:slow")
    ratings = [e["rating"] for e in r.get("log", []) if "rating" in e]
    if r.get("log"): out.append("tried")
    if ratings and sum(ratings) / len(ratings) >= 4.5: out.append("favourite")
    return out


def main() -> int:
    index, failed = [], False
    for path in sorted((ROOT / "recipes").glob("*.yaml")):
        r = yaml.safe_load(path.read_text())
        for e in r.get("log", []):  # yaml turns dates into date objects
            if isinstance(e.get("date"), date):
                e["date"] = e["date"].isoformat()
        errs = validate(path, r)
        if errs:
            failed = True
            print(f"✗ {path.name}")
            for e in errs:
                print(f"    {e}")
            continue
        flat = [f"{f}:{v}" for f, val in r["tags"].items()
                for v in (val if isinstance(val, list) else [val])]
        index.append({
            "id": r["id"], "title": r["title"], "source_lang": r["source_lang"],
            "file": f"recipes/{path.name}",
            "time_total": r["time"]["active"] + r["time"]["passive"],
            "tags": flat + derived(r),
        })
    if failed:
        return 1
    out = json.dumps(index, indent=2, ensure_ascii=False) + "\n"
    target = ROOT / "index.json"
    if "--check" in sys.argv:
        if not target.exists() or target.read_text() != out:
            print("index.json is stale, run scripts/build_index.py")
            return 1
    else:
        target.write_text(out)
    print(f"✓ {len(index)} recipes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
