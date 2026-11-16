#!/usr/bin/env python3
"""Build MapX style paste guides: source_attribute + value→color lookup + sidecars.

Reads mapx_styles/vector/_conversion_report.csv and each *.json style, optionally
re-parses SLD range filters for min/max cuts. Does NOT alter MapX style JSON schema.
"""

from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
STYLE_DIR = HERE / "mapx_styles" / "vector"
REPORT = STYLE_DIR / "_conversion_report.csv"
GEONODE_MAPX = HERE.parent


def localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def text(elem: ET.Element | None, default: str = "") -> str:
    if elem is None or elem.text is None:
        return default
    return elem.text.strip()


def resolve_style_path(style_file: str) -> Path | None:
    if not style_file:
        return None
    raw = style_file.replace("/", "\\")
    candidates = [
        HERE / raw.replace("sustainable_caucasus_archive\\", ""),
        GEONODE_MAPX / raw,
        HERE / raw,
        Path(raw),
    ]
    if "sustainable_caucasus_archive" in raw:
        tail = raw.split("sustainable_caucasus_archive\\", 1)[-1]
        candidates.insert(0, HERE / tail)
    for c in candidates:
        if c.exists():
            return c
    return None


def parse_range_cuts(sld_path: Path) -> list[dict]:
    """Extract per-rule range bounds from SLD (Greater/Less/Between)."""
    try:
        root = ET.parse(sld_path).getroot()
    except ET.ParseError:
        return []

    cuts = []
    for rule in root.iter():
        if localname(rule.tag) != "Rule":
            continue
        title_el = None
        for e in rule.iter():
            if localname(e.tag) == "Title":
                title_el = e
                break
        name_el = None
        for e in list(rule):
            if localname(e.tag) == "Name":
                name_el = e
                break
        label = text(title_el) or text(name_el)

        filt = None
        for e in rule.iter():
            if localname(e.tag) == "Filter":
                filt = e
                break
        if filt is None:
            continue

        attr = ""
        mins: list[float] = []
        maxs: list[float] = []
        for e in filt.iter():
            ln = localname(e.tag)
            if ln == "PropertyName" and not attr:
                attr = text(e)
            if ln in {
                "PropertyIsGreaterThan",
                "PropertyIsGreaterThanOrEqualTo",
                "PropertyIsLessThan",
                "PropertyIsLessThanOrEqualTo",
                "PropertyIsBetween",
            }:
                lits = []
                for c in e.iter():
                    if localname(c.tag) == "Literal" and text(c):
                        try:
                            lits.append(float(text(c)))
                        except ValueError:
                            pass
                if ln.startswith("PropertyIsGreater"):
                    mins.extend(lits)
                elif ln.startswith("PropertyIsLess"):
                    maxs.extend(lits)
                elif ln == "PropertyIsBetween" and len(lits) >= 2:
                    mins.append(lits[0])
                    maxs.append(lits[1])

        if not mins and not maxs and not label:
            continue

        # color from symbolizer
        color = ""
        for e in rule.iter():
            if localname(e.tag) in {"CssParameter", "SvgParameter"}:
                n = e.attrib.get("name", "")
                if n in {"fill", "stroke"} and text(e).startswith("#"):
                    color = text(e).lower()
                    if n == "fill":
                        break

        cuts.append(
            {
                "label": label,
                "attribute": attr,
                "min": min(mins) if mins else "",
                "max": max(maxs) if maxs else "",
                "min_inclusive": True,  # approximate; SLD mixes >/≥
                "max_inclusive": True,
                "color": color,
            }
        )
    return cuts


def how_to_paste(kind: str, status: str, attr: str) -> str:
    if status == "css_skip":
        return "GeoCSS — style manually in MapX; no JSON paste"
    if kind == "range" or status == "partial":
        return (
            f"RANGE: set Source attribute to `{attr}`; do NOT rely on categorical JSON values "
            f"(labels like 1-20 are not field values). Use Auto style / intervals with colors "
            f"from lookup/styleinfo; see range_min/range_max columns."
        )
    if kind == "categorical":
        return (
            f"1) Set Source attribute = `{attr}`  2) Paste JSON  "
            f"3) Check each Value matches dropdown (not 'all')"
        )
    if kind == "single":
        return (
            "Single symbol: paste JSON for color; Source attribute optional "
            "(one rule applies to all features)"
        )
    return "See notes; paste carefully"


def paste_categorical_ok(kind: str, status: str) -> str:
    if status == "css_skip":
        return "no"
    if kind == "range" or status == "partial":
        return "no"
    if kind in {"categorical", "single"}:
        return "yes"
    return "no"


def main() -> None:
    rows = list(csv.DictReader(REPORT.open(encoding="utf-8-sig")))
    guide_rows = []
    lookup_rows = []
    range_count = 0

    for row in rows:
        name = row["geonode_name"]
        kind = (row.get("kind") or "").strip()
        status = (row.get("status") or "").strip()
        attr = (row.get("style_attribute") or "").strip()
        mapx_id = (row.get("mapx_id") or "").strip()
        n_rules = int(row.get("n_rules") or 0)
        style_file = row.get("style_file") or ""
        json_rel = row.get("output_json") or ""
        json_path = STYLE_DIR / f"{name}.json"

        rules_out = []
        range_cuts: list[dict] = []

        if json_path.exists():
            style = json.loads(json_path.read_text(encoding="utf-8"))
            for i, rule in enumerate(style.get("rules") or [], start=1):
                rules_out.append(
                    {
                        "value": rule.get("value", ""),
                        "label_en": rule.get("label_en", ""),
                        "color": rule.get("color", ""),
                        "opacity": rule.get("opacity", ""),
                        "size": rule.get("size", ""),
                    }
                )
                lookup_rows.append(
                    {
                        "geonode_name": name,
                        "mapx_id": mapx_id,
                        "kind": kind,
                        "source_attribute": attr,
                        "rule_order": i,
                        "value": rule.get("value", ""),
                        "label_en": rule.get("label_en", ""),
                        "color": rule.get("color", ""),
                        "opacity": rule.get("opacity", ""),
                        "size": rule.get("size", ""),
                        "range_min": "",
                        "range_max": "",
                        "paste_json_as_categorical": paste_categorical_ok(kind, status),
                    }
                )

        if kind == "range" or status == "partial":
            range_count += 1
            sld = resolve_style_path(style_file)
            if sld and sld.suffix.lower() == ".sld":
                range_cuts = parse_range_cuts(sld)
                if range_cuts and not attr:
                    attr = range_cuts[0].get("attribute") or attr
                # enrich lookup with min/max by matching label/value
                by_label = {c["label"]: c for c in range_cuts if c.get("label")}
                for lr in lookup_rows:
                    if lr["geonode_name"] != name:
                        continue
                    cut = by_label.get(lr["value"]) or by_label.get(lr["label_en"])
                    if cut:
                        lr["range_min"] = cut["min"]
                        lr["range_max"] = cut["max"]
                        if cut.get("attribute"):
                            lr["source_attribute"] = cut["attribute"]
                            attr = attr or cut["attribute"]

        paste_ok = paste_categorical_ok(kind, status)
        guide_rows.append(
            {
                "geonode_name": name,
                "mapx_id": mapx_id,
                "status": status,
                "kind": kind,
                "geometry": row.get("geometry") or "",
                "source_attribute": attr,
                "n_rules": n_rules or len(rules_out),
                "paste_json_as_categorical": paste_ok,
                "how_to_paste": how_to_paste(kind, status, attr or "(none)"),
                "style_json": f"{name}.json" if json_path.exists() else "",
                "styleinfo_json": f"{name}.styleinfo.json" if json_path.exists() or status == "css_skip" else "",
                "notes": row.get("notes") or "",
            }
        )

        # sidecar styleinfo
        info = {
            "geonode_name": name,
            "mapx_id": mapx_id,
            "kind": kind or status,
            "status": status,
            "source_attribute": attr,
            "paste_json_as_categorical": paste_ok == "yes",
            "geometry": row.get("geometry") or "",
            "style_json": f"{name}.json" if json_path.exists() else None,
            "how_to_paste": how_to_paste(kind, status, attr or "(none)"),
            "rules": rules_out,
        }
        if range_cuts:
            info["range_cuts"] = [
                {
                    "label": c["label"],
                    "min": c["min"],
                    "max": c["max"],
                    "color": c["color"],
                    "attribute": c["attribute"],
                }
                for c in range_cuts
            ]
            info["warning"] = (
                "Numeric range style from SLD. MapX categorical Values like "
                "'1-20' will show as 'all' because they are not attribute values. "
                f"Set Source attribute to '{attr}' and apply interval/Auto style "
                "using range_cuts colors."
            )
        elif status == "css_skip":
            info["warning"] = "GeoCSS source — no MapX JSON generated."
        elif kind == "categorical":
            info["warning"] = (
                f"In MapX choose Source attribute = '{attr}', then paste JSON. "
                "Each rules[].value must match a real attribute value in the dropdown."
            )
        elif kind == "single":
            info["warning"] = "Single-symbol layer; one color for all features."

        (STYLE_DIR / f"{name}.styleinfo.json").write_text(
            json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    # write CSVs
    guide_path = STYLE_DIR / "_style_paste_guide.csv"
    with guide_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "geonode_name",
                "mapx_id",
                "status",
                "kind",
                "geometry",
                "source_attribute",
                "n_rules",
                "paste_json_as_categorical",
                "how_to_paste",
                "style_json",
                "styleinfo_json",
                "notes",
            ],
        )
        w.writeheader()
        w.writerows(guide_rows)

    lookup_path = STYLE_DIR / "_style_rules_lookup.csv"
    with lookup_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "geonode_name",
                "mapx_id",
                "kind",
                "source_attribute",
                "rule_order",
                "value",
                "label_en",
                "color",
                "opacity",
                "size",
                "range_min",
                "range_max",
                "paste_json_as_categorical",
            ],
        )
        w.writeheader()
        w.writerows(lookup_rows)

    readme = STYLE_DIR / "_PASTE_README.md"
    n_cat = sum(1 for r in guide_rows if r["paste_json_as_categorical"] == "yes")
    n_range = sum(1 for r in guide_rows if r["kind"] == "range" or r["status"] == "partial")
    n_skip = sum(1 for r in guide_rows if r["status"] == "css_skip")
    readme.write_text(
        f"""# MapX style paste guide

## Problem

MapX style JSON only has `rules[].value` + color. The **Source attribute** is chosen
separately in the MapX UI. If `value` is not a real value of that attribute, the
dropdown shows `all` (common for numeric range layers).

## Files

| File | Use |
|------|-----|
| `_style_paste_guide.csv` | Per layer: **source_attribute**, kind, paste yes/no |
| `_style_rules_lookup.csv` | Per rule: attribute → value → label → **color** (+ range_min/max) |
| `<layer>.styleinfo.json` | Same info next to each style JSON |
| `<layer>.json` | Paste into MapX style editor (JSON tab) |

## Counts

- Layers in guide: **{len(guide_rows)}**
- Paste as categorical: **{n_cat}**
- Range / partial (do not paste as categorical values): **{n_range}**
- GeoCSS skip: **{n_skip}**

## Workflow (categorical — e.g. `protect_areas`)

1. Open `_style_paste_guide.csv` → find layer → copy **source_attribute** (e.g. `IUCN_CAT`).
2. In MapX: set **Source attribute** to that field.
3. Paste `<layer>.json` in the style JSON tab (or apply rules).
4. Check each **Value** matches the dropdown (`Ia`, `Ib`, …) — not `all`.
5. If needed, use `_style_rules_lookup.csv` filtered by `geonode_name` to map value ↔ color.

## Workflow (range — e.g. `caucasus_population_density_2020`)

1. Source attribute = `pop_densit` (numeric).
2. **Do not** expect categorical paste of `"1-20"` to work — those strings are legend labels, not field values.
3. Open `<layer>.styleinfo.json` → `range_cuts` (min/max/color) or lookup columns `range_min` / `range_max`.
4. In MapX use **Auto style** / interval classification on that attribute and assign the listed colors.

## Examples

- `protect_areas` → Source attribute **`IUCN_CAT`** → values `Ia`, `Ib`, `II`, …
- `roads_caucasus_select` → **`fclass`** → `motorway`, `trunk`, `primary`, `secondary`
- `caucasus_population_density_2020` → **`pop_densit`** → range cuts (partial); paste_json_as_categorical = **no**
- `IFL_2013_Caucasus` → single symbol (one color); source attribute optional

## Spanish (corto)

1. Mira `_style_paste_guide.csv` → columna **source_attribute**.
2. En MapX elige ese atributo como Source attribute.
3. Si `paste_json_as_categorical=yes`, pega el JSON y verifica Value ≠ `all`.
4. Si es `range` / `no`, usa cortes `range_min`/`range_max` + colores (Auto style).
""",
        encoding="utf-8",
    )

    print(f"guide: {guide_path} ({len(guide_rows)} layers)")
    print(f"lookup: {lookup_path} ({len(lookup_rows)} rules)")
    print(f"readme: {readme}")
    print(f"styleinfo sidecars: {len(guide_rows)}")
    print(f"range/partial layers: {n_range}")


if __name__ == "__main__":
    main()
