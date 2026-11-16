#!/usr/bin/env python3
"""Convert GeoServer SLD styles to MapX categorical JSON styles.

Reads triage/publication_catalog.csv (vector + publish=yes), parses each
style_file SLD, and writes mapx_styles/vector/<layer>.json plus
_conversion_report.csv.
"""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


HERE = Path(__file__).resolve().parent
CATALOG = HERE / "triage" / "publication_catalog.csv"
OUT_DIR = HERE / "mapx_styles" / "vector"

# Local path prefixes used in the catalog -> resolve under HERE.parent or HERE
GEONODE_MAPX = HERE.parent

EMPTY_LABELS = {
    "label_fr": "",
    "label_es": "",
    "label_ar": "",
    "label_ru": "",
    "label_zh": "",
    "label_de": "",
    "label_bn": "",
    "label_fa": "",
    "label_ps": "",
}

TITLE_LEGEND = {
    "en": "Legend",
    "fr": "",
    "es": "",
    "ar": "",
    "ru": "",
    "zh": "",
    "de": "",
    "bn": "",
    "fa": "",
    "ps": "",
}

ZOOM = {
    "zoomMin": 0,
    "zoomMax": 22,
    "sizeFactorZoomMax": 0,
    "sizeFactorZoomMin": 0,
    "sizeFactorZoomExponent": 1,
}


def localname(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def findall(elem: ET.Element, name: str) -> list[ET.Element]:
    return [e for e in elem.iter() if localname(e.tag) == name]


def find(elem: ET.Element, name: str) -> ET.Element | None:
    for e in elem.iter():
        if localname(e.tag) == name:
            return e
    return None


def text(elem: ET.Element | None, default: str = "") -> str:
    if elem is None or elem.text is None:
        return default
    return elem.text.strip()


def param_color(symbolizer: ET.Element, kind: str) -> str | None:
    """kind: fill | stroke"""
    for param in list(symbolizer.iter()):
        ln = localname(param.tag)
        if ln not in {"CssParameter", "SvgParameter"}:
            continue
        name = param.attrib.get("name", "")
        if name == kind or name == f"{kind}":
            val = (param.text or "").strip()
            if val.startswith("#"):
                return val.lower()
    return None


def param_float(symbolizer: ET.Element, name: str, default: float | None = None) -> float | None:
    for param in list(symbolizer.iter()):
        if localname(param.tag) not in {"CssParameter", "SvgParameter"}:
            continue
        if param.attrib.get("name") == name:
            try:
                return float((param.text or "").strip())
            except ValueError:
                return default
    return default


def opacity_from(symbolizer: ET.Element, fill: bool) -> float:
    key = "fill-opacity" if fill else "stroke-opacity"
    val = param_float(symbolizer, key)
    if val is None:
        # sometimes just "opacity"
        val = param_float(symbolizer, "opacity")
    if val is None:
        return 0.7 if fill else 1.0
    return max(0.0, min(1.0, val))


def detect_geometry(rule: ET.Element) -> str:
    tags = {localname(e.tag) for e in rule.iter()}
    if "PointSymbolizer" in tags:
        return "point"
    if "LineSymbolizer" in tags:
        return "line"
    if "PolygonSymbolizer" in tags:
        return "polygon"
    return "polygon"


def extract_filter_info(rule: ET.Element) -> dict:
    """Return {kind, attribute, value, label, notes} from a Rule filter."""
    filt = None
    for e in rule:
        if localname(e.tag) == "Filter":
            filt = e
            break
    # Filter may be nested deeper in some exports
    if filt is None:
        filters = findall(rule, "Filter")
        filt = filters[0] if filters else None

    title = text(find(rule, "Title")) or text(find(rule, "Name")) or "Class"
    name = text(find(rule, "Name")) or title

    if filt is None:
        return {
            "kind": "single",
            "attribute": "",
            "value": name or "all",
            "label": title or name or "all",
            "notes": [],
        }

    # EqualTo
    for eq in findall(filt, "PropertyIsEqualTo"):
        prop = text(find(eq, "PropertyName"))
        lit = text(find(eq, "Literal"))
        if prop:
            return {
                "kind": "categorical",
                "attribute": prop,
                "value": lit,
                "label": title or lit,
                "notes": [],
            }

    # Not equal / other equality variants
    for eq in findall(filt, "PropertyIsNotEqualTo"):
        prop = text(find(eq, "PropertyName"))
        lit = text(find(eq, "Literal"))
        if prop:
            return {
                "kind": "categorical",
                "attribute": prop,
                "value": lit,
                "label": title or f"≠ {lit}",
                "notes": ["PropertyIsNotEqualTo approximated as categorical value"],
            }

    # Range: And of Greater/Less
    props = findall(filt, "PropertyName")
    lits = findall(filt, "Literal")
    prop_names = [text(p) for p in props if text(p)]
    lit_vals = [text(l) for l in lits if text(l)]
    range_ops = [
        localname(e.tag)
        for e in filt.iter()
        if localname(e.tag).startswith("PropertyIs")
        and any(
            x in localname(e.tag)
            for x in (
                "Greater",
                "Less",
                "Between",
            )
        )
    ]
    if range_ops or (prop_names and any(op in "".join(range_ops) for op in ())):
        pass
    if any(
        localname(e.tag)
        in {
            "PropertyIsGreaterThan",
            "PropertyIsGreaterThanOrEqualTo",
            "PropertyIsLessThan",
            "PropertyIsLessThanOrEqualTo",
            "PropertyIsBetween",
        }
        for e in filt.iter()
    ):
        attr = prop_names[0] if prop_names else ""
        label = title or name
        # Prefer title like "1-20" as value for MapX categorical paste
        value = label
        return {
            "kind": "range",
            "attribute": attr,
            "value": value,
            "label": label,
            "notes": [
                "range filter; MapX rule value uses class label — "
                "confirm attribute/mode in MapX UI"
            ],
            "literals": lit_vals,
        }

    # Like / Null
    return {
        "kind": "partial",
        "attribute": prop_names[0] if prop_names else "",
        "value": title or name,
        "label": title or name,
        "notes": ["complex/unsupported filter; value = rule title"],
    }


def extract_symbol(rule: ET.Element, geom: str) -> dict:
    color = "#808080"
    opacity = 0.7
    size = 7
    notes = []

    if geom == "polygon":
        poly = find(rule, "PolygonSymbolizer")
        if poly is not None:
            fill = param_color(poly, "fill")
            stroke = param_color(poly, "stroke")
            color = fill or stroke or color
            opacity = opacity_from(poly, fill=True)
            sw = param_float(poly, "stroke-width")
            size = int(sw) if sw and sw >= 1 else 1
            if find(poly, "ExternalGraphic") or find(poly, "Mark"):
                notes.append("pattern/mark fill not fully represented")
    elif geom == "line":
        line = find(rule, "LineSymbolizer")
        if line is not None:
            stroke = param_color(line, "stroke")
            color = stroke or color
            opacity = opacity_from(line, fill=False)
            sw = param_float(line, "stroke-width", 2) or 2
            size = max(1, int(round(sw)))
    else:  # point
        point = find(rule, "PointSymbolizer")
        if point is not None:
            fill = param_color(point, "fill")
            stroke = param_color(point, "stroke")
            color = fill or stroke or "#ff0000"
            opacity = opacity_from(point, fill=True)
            size_el = find(point, "Size")
            if size_el is not None and text(size_el):
                try:
                    size = int(float(text(size_el)))
                except ValueError:
                    size = 10
            else:
                size = 10
            if find(point, "ExternalGraphic") is not None:
                notes.append("ExternalGraphic SVG not mapped; sprite=none + color fallback")
                color = color if color != "#808080" else "#c0392b"

    if not color.startswith("#"):
        color = "#808080"
        notes.append("non-hex color replaced")
    # normalize #rgb -> #rrggbb
    if len(color) == 4:
        color = "#" + "".join(c * 2 for c in color[1:])

    return {"color": color.lower(), "opacity": opacity, "size": size, "notes": notes}


def mapx_type(geom: str) -> str:
    return {"point": "circle", "line": "line", "polygon": "fill"}.get(geom, "fill")


def empty_labels_rule(value: str, label_en: str, color: str, opacity: float, size: int) -> dict:
    return {
        "value": value,
        "label_en": label_en,
        **EMPTY_LABELS,
        "color": color,
        "opacity": opacity,
        "size": size,
        "sprite": "none",
    }


def build_mapx_json(rules_out: list[dict], geom: str, legend_title: str = "Legend") -> dict:
    title = dict(TITLE_LEGEND)
    title["en"] = legend_title or "Legend"
    custom_obj = {
        "enable": False,
        "paint": {},
        "layout": {},
        "filter": [">", ["get", "gid"], 0],
        "minzoom": 0,
        "maxzoom": 22,
        "type": mapx_type(geom),
    }
    return {
        "nulls": [
            empty_labels_rule("", "No data", "#a9a9a9", 0.7, 7 if geom == "point" else 1)
        ],
        "rules": rules_out,
        "zoomConfig": dict(ZOOM),
        "reverseLayer": False,
        "showSymbolLabel": False,
        "hideNulls": True,
        "titleLegend": title,
        "custom": {"json": json.dumps(custom_obj, indent=2)},
    }


def parse_sld(path: Path) -> dict:
    """Parse one SLD file -> conversion result."""
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return {
            "status": "failed",
            "error": f"XML parse error: {exc}",
            "rules": [],
            "geometry": "",
            "style_attribute": "",
            "kind": "",
            "notes": [],
            "mapx": None,
        }

    root = tree.getroot()
    rules_el = [e for e in root.iter() if localname(e.tag) == "Rule"]
    if not rules_el:
        return {
            "status": "failed",
            "error": "no Rule elements",
            "rules": [],
            "geometry": "",
            "style_attribute": "",
            "kind": "",
            "notes": [],
            "mapx": None,
        }

    geoms = [detect_geometry(r) for r in rules_el]
    # majority geometry
    geom = max(set(geoms), key=geoms.count)

    parsed_rules = []
    notes_all: list[str] = []
    kinds = set()
    attrs = set()

    for rule in rules_el:
        info = extract_filter_info(rule)
        g = detect_geometry(rule)
        sym = extract_symbol(rule, g)
        kinds.add(info["kind"])
        if info.get("attribute"):
            attrs.add(info["attribute"])
        notes_all.extend(info.get("notes") or [])
        notes_all.extend(sym.get("notes") or [])
        parsed_rules.append(
            {
                "value": str(info["value"]),
                "label_en": str(info["label"]),
                "color": sym["color"],
                "opacity": sym["opacity"],
                "size": sym["size"],
            }
        )

    # Deduplicate by value keeping first
    seen = set()
    unique_rules = []
    for r in parsed_rules:
        key = r["value"]
        if key in seen:
            continue
        seen.add(key)
        unique_rules.append(
            empty_labels_rule(
                r["value"], r["label_en"], r["color"], r["opacity"], r["size"]
            )
        )

    if not unique_rules:
        return {
            "status": "failed",
            "error": "no extractable rules",
            "rules": [],
            "geometry": geom,
            "style_attribute": "",
            "kind": "",
            "notes": notes_all,
            "mapx": None,
        }

    kind = "categorical"
    if kinds == {"single"}:
        kind = "single"
    elif "range" in kinds:
        kind = "range"
    elif "partial" in kinds:
        kind = "partial"
    elif "categorical" in kinds:
        kind = "categorical"

    status = "ok"
    if kind in {"range", "partial"}:
        status = "partial"
    if kind == "single" and len(unique_rules) == 1:
        status = "ok"

    style_attribute = next(iter(attrs), "")
    if kind == "single":
        style_attribute = style_attribute or ""

    # Prefer NamedLayer/UserStyle Name over first Rule Title
    legend = "Legend"
    for layer in root.iter():
        if localname(layer.tag) != "NamedLayer":
            continue
        for child in list(layer):
            if localname(child.tag) == "Name" and text(child):
                legend = text(child)
                break
        break
    if legend == "Legend":
        for us in root.iter():
            if localname(us.tag) != "UserStyle":
                continue
            for child in list(us):
                if localname(child.tag) == "Name" and text(child):
                    legend = text(child)
                    break
            break
    mapx = build_mapx_json(unique_rules, geom, legend_title=legend)

    return {
        "status": status,
        "error": "",
        "rules": unique_rules,
        "geometry": geom,
        "style_attribute": style_attribute,
        "kind": kind,
        "notes": sorted(set(notes_all)),
        "mapx": mapx,
        "n_rules": len(unique_rules),
    }


def resolve_style_path(style_file: str) -> Path | None:
    if not style_file:
        return None
    raw = style_file.replace("/", "\\")
    candidates = [
        GEONODE_MAPX / raw,
        HERE / raw.replace("sustainable_caucasus_archive\\", ""),
        HERE / raw,
        Path(raw),
    ]
    # Also try relative from HERE if path starts with sustainable_caucasus_archive
    if "sustainable_caucasus_archive" in raw:
        tail = raw.split("sustainable_caucasus_archive\\", 1)[-1]
        candidates.insert(0, HERE / tail)
        candidates.insert(0, GEONODE_MAPX / "sustainable_caucasus_archive" / tail)
    for c in candidates:
        if c.exists():
            return c
    return None


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(CATALOG.open(encoding="utf-8-sig")))
    vectors = [
        r
        for r in rows
        if (r.get("layer_kind") or "") == "vector" and (r.get("publish") or "") == "yes"
    ]

    report = []
    for row in vectors:
        name = row["geonode_name"]
        style_file = row.get("style_file") or ""
        out_json = OUT_DIR / f"{name}.json"
        entry = {
            "geonode_name": name,
            "mapx_id": row.get("mapx_id") or "",
            "style_file": style_file,
            "status": "",
            "kind": "",
            "geometry": "",
            "style_attribute": "",
            "n_rules": 0,
            "output_json": "",
            "notes": "",
            "error": "",
        }

        if style_file.lower().endswith(".css"):
            entry["status"] = "css_skip"
            entry["notes"] = "GeoCSS not converted; style manually in MapX"
            report.append(entry)
            continue

        path = resolve_style_path(style_file)
        if path is None:
            entry["status"] = "failed"
            entry["error"] = f"style file not found: {style_file}"
            report.append(entry)
            continue

        result = parse_sld(path)
        entry["status"] = result["status"]
        entry["kind"] = result.get("kind") or ""
        entry["geometry"] = result.get("geometry") or ""
        entry["style_attribute"] = result.get("style_attribute") or ""
        entry["n_rules"] = result.get("n_rules") or len(result.get("rules") or [])
        entry["notes"] = "; ".join(result.get("notes") or [])
        entry["error"] = result.get("error") or ""

        if result.get("mapx"):
            out_json.write_text(
                json.dumps(result["mapx"], indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            entry["output_json"] = str(
                Path("sustainable_caucasus_archive") / "mapx_styles" / "vector" / f"{name}.json"
            )
        report.append(entry)

    report_path = OUT_DIR / "_conversion_report.csv"
    fields = [
        "geonode_name",
        "mapx_id",
        "style_file",
        "status",
        "kind",
        "geometry",
        "style_attribute",
        "n_rules",
        "output_json",
        "notes",
        "error",
    ]
    with report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(report)

    # summary
    from collections import Counter

    counts = Counter(r["status"] for r in report)
    lines = [
        "SLD -> MapX JSON conversion report",
        f"Vector layers: {len(report)}",
        f"Status counts: {dict(counts)}",
        f"Output dir: {OUT_DIR}",
        "",
    ]
    for status in ("ok", "partial", "css_skip", "failed"):
        names = [r["geonode_name"] for r in report if r["status"] == status]
        if not names:
            continue
        lines.append(f"=== {status} ({len(names)}) ===")
        for n in names:
            rec = next(r for r in report if r["geonode_name"] == n)
            lines.append(
                f"  {n}  |  {rec['kind']}  |  attr={rec['style_attribute'] or '-'}  |  "
                f"rules={rec['n_rules']}  |  {rec['geometry']}"
            )
        lines.append("")

    summary = "\n".join(lines)
    (OUT_DIR / "_conversion_summary.txt").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
