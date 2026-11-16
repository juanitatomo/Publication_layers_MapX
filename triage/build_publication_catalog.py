#!/usr/bin/env python3
"""Build a unique MapX publication catalog from P1 + existing MapX WMS views.

Reads:
  - caucasus_script.csv (MapX view ids pointing at GeoNode WMS)
  - layer_characterization.csv
  - source_availability.csv
  - style_manifest.csv

Writes:
  - publication_catalog.csv
  - publication_catalog_summary.txt
  - publication_skipped.csv
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


HERE = Path(__file__).resolve().parent
SCRIPT_CSV = HERE / "caucasus_script.csv"
CHAR_CSV = HERE / "layer_characterization.csv"
SOURCE_CSV = HERE / "source_availability.csv"
STYLE_CSV = HERE / "geoserver" / "geoserver" / "style_manifest.csv"
STYLES_ROOT = HERE / "geoserver" / "geoserver"

LAYER_RE = re.compile(r"layers=geonode(?::|%3A|%3a)([^&]+)", re.I)

TEST_TITLES = {"test caucasus", "test"}
SKIP_MAPX_IDS = {
    "MX-VO1UM-OO4GR-SW9VZ",  # Test Caucasus
    "MX-YWU5S-ND8K2-BK04Z",  # test
    "MX-8Z88D-P09HB-07Y4C",  # duplicate POI culture
    "MX-7UKB7-SEHW5-Z7HN9",  # landcover 2010 with empty layers=
}

# Title in MapX said 2005/2010 but WMS still requested ESA2000.
TITLE_LAYER_FIX = {
    "MX-I4VTO-9X4S1-VQQPE": "ESA2005_Cauc",  # titled Land Cover 2005
    "MX-2FANI-UZZD6-QHA6V": "ESA2010_Cauc",  # titled Land Cover 2010
}

NAME_REMAP = {
    "Forest_height_2019_NAFR_Caucasus_Ecoregion0": "Forest_height_2019_NAFR_Caucasus_Ecoregion",
}

EMPTY_URL_LAYER = {
    "MX-QADA7-ZALP5-69X48": "rad_dur_jan",
}

PREFERRED_POI_CULTURE_ID = "MX-YAE4P-E1XUK-R8PHH"


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def extract_layer(url: str) -> str:
    if not url:
        return ""
    match = LAYER_RE.search(url)
    if match:
        return unquote(match.group(1)).strip()
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    for key in params:
        if key.lower() == "layers":
            raw = params[key][0]
            return raw.split(":")[-1].strip()
    return ""


def prefer_source(source_note: str) -> str:
    if not source_note or source_note.startswith("PostGIS") or source_note.startswith("GeoTIFF expected"):
        return ""
    parts = [p.strip() for p in source_note.split(";") if p.strip()]
    if not parts:
        return ""

    def rank(path: str) -> tuple[int, int]:
        lower = path.lower().replace("/", "\\")
        score = 50
        if r"rasters\geoserver" in lower and lower.endswith(".geotiff"):
            score = 0
        elif r"rasters\geoserver" in lower:
            score = 1
        elif lower.endswith(".gpkg"):
            score = 2
        elif r"geonode_importer" in lower:
            score = 3
        return (score, len(path))

    parts.sort(key=rank)
    return parts[0]


def archive_rel(path: Path) -> str:
    try:
        return str(Path("sustainable_caucasus_archive") / path.relative_to(HERE))
    except ValueError:
        return str(path)


def find_style_on_disk(name: str, original_filename: str = "", style_file: str = "") -> Path | None:
    folder = STYLES_ROOT / "styles" / "geonode"
    global_folder = STYLES_ROOT / "styles" / "global"
    candidates = []
    if style_file:
        candidates.append(STYLES_ROOT / style_file.replace("/", "\\"))
        candidates.append(STYLES_ROOT / style_file.replace("geonode:", "geonode_").replace("/", "\\"))
    if original_filename:
        candidates.append(folder / original_filename)
        candidates.append(folder / original_filename.replace("geonode:", "geonode_"))
    for stem in (f"geonode_{name}", name, f"geonode:{name}"):
        for ext in (".sld", ".css"):
            candidates.append(folder / f"{stem}{ext}")
            candidates.append(global_folder / f"{stem}{ext}")
    for path in candidates:
        if path.exists():
            return path
    return None


def style_for_layer(name: str, styles: list[dict]) -> tuple[str, str, str]:
    qualified = f"geonode:{name}"
    default = None
    alternate = None
    by_name = None
    for row in styles:
        layers = (row.get("layers") or "").strip()
        role = (row.get("roles") or "").lower()
        style_name = row.get("style_name") or ""
        layer_tokens = [t.strip() for t in layers.replace(";", ",").split(",") if t.strip()]
        if qualified in layer_tokens or name in layer_tokens:
            if role == "default":
                default = row
            elif role == "alternate" and alternate is None:
                alternate = row
        if style_name in {name, qualified, f"geonode_{name}"}:
            by_name = row
    chosen = default or by_name or alternate
    role = (chosen.get("roles") if chosen else "") or ""
    original = (chosen.get("original_filename") if chosen else "") or ""
    rel = (chosen.get("style_file") if chosen else "") or ""
    path = find_style_on_disk(name, original, rel)
    if path:
        return archive_rel(path), role or "default", "ok"
    if rel:
        return rel.replace("geonode:", "geonode_"), role, "style_file_listed"
    return "", "", "style_missing"


def parse_script_rows() -> tuple[list[dict], list[dict]]:
    views = []
    skipped = []
    for row in load_csv(SCRIPT_CSV):
        mapx_id = (row.get("id") or "").strip()
        title = (row.get("name") or "").strip()
        url = (row.get("url") or "").strip()
        raw_layer = extract_layer(url)
        url_status = "ok"
        notes = []

        if mapx_id in SKIP_MAPX_IDS or title.lower() in TEST_TITLES:
            skipped.append(
                {
                    "mapx_id": mapx_id,
                    "mapx_title": title,
                    "raw_layer": raw_layer,
                    "reason": "test_or_duplicate_or_broken_wms",
                    "url": url,
                }
            )
            continue

        layer = raw_layer
        if mapx_id in TITLE_LAYER_FIX:
            layer = TITLE_LAYER_FIX[mapx_id]
            url_status = "wrong_layer"
            notes.append(f"WMS requested {raw_layer}; title implies {layer}")
        elif mapx_id in EMPTY_URL_LAYER:
            layer = EMPTY_URL_LAYER[mapx_id]
            url_status = "empty"
            notes.append("MapX URL empty; keep view id and attach local source")
        elif not url:
            url_status = "empty"
            notes.append("MapX URL empty; keep view id and attach local source")
        elif not raw_layer:
            url_status = "empty"
            notes.append("WMS URL has no layers= parameter")
            skipped.append(
                {
                    "mapx_id": mapx_id,
                    "mapx_title": title,
                    "raw_layer": "",
                    "reason": "wms_missing_layers",
                    "url": url,
                }
            )
            continue

        if layer in NAME_REMAP:
            notes.append(f"remap {layer} -> {NAME_REMAP[layer]} (duplicate without local file)")
            layer = NAME_REMAP[layer]

        if not layer:
            skipped.append(
                {
                    "mapx_id": mapx_id,
                    "mapx_title": title,
                    "raw_layer": raw_layer,
                    "reason": "no_geonode_layer",
                    "url": url,
                }
            )
            continue

        views.append(
            {
                "mapx_id": mapx_id,
                "mapx_title": title,
                "geonode_name": layer,
                "raw_layer": raw_layer,
                "url_status": url_status,
                "notes": notes,
                "url": url,
            }
        )
    return views, skipped


def main() -> None:
    chars = {r["name"]: r for r in load_csv(CHAR_CSV)}
    sources = {r["name"]: r for r in load_csv(SOURCE_CSV)}
    styles = load_csv(STYLE_CSV)
    p1_names = {name for name, rec in chars.items() if rec.get("tier") == "P1"}

    views, skipped = parse_script_rows()

    by_layer: dict[str, list[dict]] = defaultdict(list)
    for view in views:
        by_layer[view["geonode_name"]].append(view)

    all_names = set(p1_names) | set(by_layer)
    catalog = []

    for name in sorted(all_names, key=str.lower):
        char = chars.get(name, {})
        src = sources.get(name, {})
        views_for = by_layer.get(name, [])
        in_p1 = name in p1_names
        in_script = bool(views_for)
        if in_p1 and in_script:
            origin = "both"
        elif in_p1:
            origin = "p1_only"
        else:
            origin = "script_only"

        chosen = views_for[0] if views_for else None
        extra_ids = [v["mapx_id"] for v in views_for[1:]]
        notes = []
        url_status = "new"
        mapx_id = ""
        mapx_title = char.get("title") or name
        if chosen:
            mapx_id = chosen["mapx_id"]
            mapx_title = chosen["mapx_title"] or mapx_title
            url_status = chosen["url_status"]
            notes.extend(chosen["notes"])
        if extra_ids:
            notes.append("extra_mapx_ids=" + ";".join(extra_ids))

        local = prefer_source(src.get("source_note") or char.get("source_note") or "")
        source_status = src.get("source_status") or char.get("source_status") or "unknown"
        style_file, style_role, style_status = style_for_layer(name, styles)

        publish = "yes"
        if source_status.startswith("missing") and not local:
            publish = "no"
            notes.append("local source missing")
        if name.endswith("Ecoregion0"):
            publish = "no"
            notes.append("duplicate raster without file")

        catalog.append(
            {
                "geonode_name": name,
                "title": mapx_title,
                "geonode_title": char.get("title") or "",
                "layer_kind": char.get("layer_kind") or src.get("layer_kind") or "",
                "origin": origin,
                "mapx_id": mapx_id,
                "mapx_url_status": url_status,
                "extra_mapx_ids": ";".join(extra_ids),
                "local_source": local,
                "source_status": source_status,
                "srs": char.get("srs") or "",
                "theme": char.get("theme") or "",
                "tier": char.get("tier") or "",
                "style_file": style_file,
                "style_role": style_role,
                "style_status": style_status,
                "publish": publish,
                "notes": "; ".join(notes),
            }
        )

    catalog.sort(key=lambda r: (r["origin"], r["layer_kind"], r["geonode_name"]))
    fields = [
        "geonode_name",
        "title",
        "geonode_title",
        "layer_kind",
        "origin",
        "mapx_id",
        "mapx_url_status",
        "extra_mapx_ids",
        "local_source",
        "source_status",
        "srs",
        "theme",
        "tier",
        "style_file",
        "style_role",
        "style_status",
        "publish",
        "notes",
    ]
    write_csv(HERE / "publication_catalog.csv", catalog, fields)
    write_csv(
        HERE / "publication_skipped.csv",
        skipped,
        ["mapx_id", "mapx_title", "raw_layer", "reason", "url"],
    )

    def count(pred) -> int:
        return sum(1 for r in catalog if pred(r))

    lines = []
    lines.append("MapX publication catalog: P1 + existing views")
    lines.append(f"Unique datasets: {len(catalog)}")
    lines.append(f"  both:       {count(lambda r: r['origin']=='both')}")
    lines.append(f"  p1_only:    {count(lambda r: r['origin']=='p1_only')}")
    lines.append(f"  script_only:{count(lambda r: r['origin']=='script_only')}")
    lines.append(f"Publish yes:  {count(lambda r: r['publish']=='yes')}")
    lines.append(f"Publish no:   {count(lambda r: r['publish']=='no')}")
    lines.append(f"Skipped MapX views: {len(skipped)}")
    lines.append("")
    lines.append("Skipped:")
    for row in skipped:
        lines.append(f"  {row['mapx_id']}  {row['mapx_title']}  ({row['reason']})")
    lines.append("")
    for origin in ("both", "p1_only", "script_only"):
        lines.append(f"=== {origin} ===")
        for rec in catalog:
            if rec["origin"] != origin:
                continue
            mx = rec["mapx_id"] or "(new)"
            st = rec["style_file"] or "NO_STYLE"
            src = rec["local_source"] or rec["source_status"]
            lines.append(
                f"  [{rec['layer_kind'][:1].upper()}] {rec['geonode_name']}  |  "
                f"{mx}  |  {rec['mapx_url_status']}  |  {src}  |  {st}"
            )
        lines.append("")
    summary = "\n".join(lines)
    (HERE / "publication_catalog_summary.txt").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
