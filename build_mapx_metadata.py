#!/usr/bin/env python3
"""Build MapX metadata JSON for all publish=yes layers in publication_catalog.csv.

Strict 1:1 geonode_name <-> mapx_id from the catalog (never invent MX- ids).
"""

from __future__ import annotations

import csv
import json
import re
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "triage" / "publication_catalog.csv"
CHAR = HERE / "triage" / "layer_characterization.csv"
OUT_DIR = HERE / "mapx_metadata"
OVERRIDES = HERE / "mapx_metadata" / "_text_overrides.json"

EMPTY_LANG = {
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

CAUCASUS_M49 = ["ARM", "AZE", "IRN", "TUR", "RUS", "GEO"]

# Valid MapX bbox (0,0,0,0 fails isBboxMeta). Approx Caucasus ecoregion in EPSG:4326.
CAUCASUS_BBOX = {
    "lng_min": 36.0,
    "lng_max": 54.0,
    "lat_min": 35.0,
    "lat_max": 46.5,
}

DEFAULT_CONTACT = {
    "function": "Point of contact",
    "honorific": "",
    "name": "Sustainable Caucasus / MapX publication",
    "organisation": "UNEP/GRID-Geneva",
    "address": "",
    "city": "Geneva",
    "state": "",
    "postal_code": "",
    "country": "Switzerland",
    "email": "info@mapx.org",
}

THEME_TOPIC = {
    "forest": ["environment", "biota"],
    "land_cover": ["environment", "imageryBaseMapsEarthCover"],
    "biodiversity_pa": ["environment", "biota"],
    "population_socio": ["society"],
    "climate": ["climatologyMeteorologyAtmosphere"],
    "hazard": ["geoscientificInformation"],
    "elevation_mountains": ["elevation"],
    "water_glacier": ["inlandWaters", "geoscientificInformation"],
    "infrastructure": ["transportation"],
    "culture_tourism": ["society"],
    "other": ["environment"],
}

THEME_GEMET = {
    "forest": ["3406", "2519", "4612"],
    "land_cover": ["4665", "4612"],
    "biodiversity_pa": ["796", "4612", "1485"],
    "population_socio": ["6571", "1485"],
    "climate": ["1471", "4612"],
    "hazard": ["3664", "4612"],
    "elevation_mountains": ["2685", "4612"],
    "water_glacier": ["2924", "4612"],
    "infrastructure": ["8479", "4612"],
    "culture_tourism": ["1485"],
    "other": ["4612"],
}

THEME_KEYS = {
    "forest": ["forest", "forest conservation", "forest ecosystems"],
    "land_cover": ["land cover", "land use", "remote sensing"],
    "biodiversity_pa": ["protected areas", "biodiversity", "conservation"],
    "population_socio": ["population", "demography", "socioeconomic"],
    "climate": ["climate", "meteorology", "temperature"],
    "hazard": ["natural hazards", "risk", "disaster risk"],
    "elevation_mountains": ["mountains", "elevation", "topography"],
    "water_glacier": ["hydrology", "water", "rivers", "freshwater"],
    "infrastructure": ["infrastructure", "transport", "roads"],
    "culture_tourism": ["culture", "heritage", "tourism"],
    "other": ["caucasus"],
}

FIELD_LABELS = {
    "ifl_id": "Intact Forest Landscape ID",
    "IFL_ID": "Intact Forest Landscape ID",
    "ifl_id_2": "Intact Forest Landscape ID (2013)",
    "area_ha": "Area (hectares)",
    "AREA_HA": "Area (hectares)",
    "area_ha_2": "Area 2013 (hectares)",
    "area": "Area",
    "Area": "Glacier Area (km2)",
    "GIS_AREA": "GIS Area",
    "ARCID": "Arc Identifier",
    "UP_CELLS": "Upstream Cells (flow accumulation)",
    "name": "Name",
    "Name": "Name",
    "NAME": "Name",
    "fclass": "Feature Class",
    "IUCN_CAT": "IUCN Management Category",
    "pop_densit": "Population Density (people/km2)",
    "Growth_pop": "Avg Annual Population Growth (%)",
    "Urban_leve": "Urbanization Level (%)",
    "NUTS2_Popu": "Total Population (NUTS2)",
    "nbr_fires": "Number of Fires",
    "POP_1989": "Population 1989",
    "POP_2002": "Population 2002",
    "POP_2014": "Population 2014",
    "POPM2002": "Male Population 2002",
    "POPW2002": "Female Population 2002",
    "POPM2014": "Male Population 2014",
    "POPW2014": "Female Population 2014",
    "Class_Name": "Land Cover Class",
    "Status": "Status",
    "STATUS": "Status",
    "Aquifer": "Aquifer System",
    "Landuse": "Land Use Class",
    "Precipitat": "Average Annual Precipitation",
    "DangerLvl": "Avalanche Hazard Level",
    "Descriptio": "Description",
    "Dur_days": "Flood Duration (days)",
    "Thick_mm": "Flood Layer Thickness (mm)",
    "NUMERICUSE": "Runoff Thickness Class",
    "Tipe": "Landscape Type",
    "Precip_mm": "Precipitation (mm)",
    "NAME_TB": "Fault / Feature Name",
    "risk": "Debris/Mudflow Risk",
    "VALUE": "Value",
    "Value": "Value",
    "UNIT": "Unit",
    "Unit": "Unit",
    "Zone": "Seismic Zone",
    "Sun_radiat": "Average Annual Solar Radiation",
    "Sum_of_ave": "Sum Daily Temp Above 10C",
    "Temperatur": "Average Annual Temperature (C)",
    "ZoneID": "Vegetation Zone ID",
    "Wind_Speed": "Average Wind Speed (m/s)",
    "copie_de_s": "Copied field (source)",
    "copie_de_2": "Copied field (secondary)",
    "gid": "Feature ID",
    "id": "ID",
    "ID": "Identifier",
    "fid": "Feature ID",
    "fid_1": "Feature ID (secondary)",
    "objectid": "Object ID",
    "OBJECTID": "Object ID",
    "OBJECTID_1": "Object ID (secondary)",
    "Adm1_code": "Admin Level 1 Code",
    "Adm1_name": "Admin Level 1 Name",
    "Adm2_code": "Admin Level 2 Code",
    "Adm2_name": "Admin Level 2 Name",
    "Country": "Country",
    "COUNTRY": "Country",
    # RGI / glaciers
    "RGIId": "RGI Identifier",
    "GLIMSId": "GLIMS Identifier",
    "BgnDate": "Survey Start Date",
    "EndDate": "Survey End Date",
    "CenLon": "Centroid Longitude",
    "CenLat": "Centroid Latitude",
    "O1Region": "RGI First-Order Region",
    "O2Region": "RGI Second-Order Region",
    "Zmin": "Minimum Elevation (m)",
    "Zmax": "Maximum Elevation (m)",
    "Zmed": "Median Elevation (m)",
    "Slope": "Mean Slope (deg)",
    "Aspect": "Aspect (deg)",
    "Lmax": "Maximum Length (m)",
    "Connect": "Connectivity Code",
    "Form": "Glacier Form",
    "TermType": "Terminus Type",
    "Surging": "Surging Status",
    "Linkages": "Linkages",
    # OSM / roads
    "osm_id": "OpenStreetMap ID",
    "bridge": "Bridge",
    "tunnel": "Tunnel",
    "ref": "Route Reference",
    "oneway": "One-way",
    "maxspeed": "Maximum Speed",
    "layer": "Layer",
    # geometry helpers
    "Shape_Leng": "Shape Length",
    "Shape_Length": "Shape Length",
    "Shape_Area": "Shape Area",
    "Shape_Le_1": "Shape Length (secondary)",
    "area_m2": "Area (m²)",
    "area_km2": "Area (km²)",
    "area_km2_1": "Area (km², secondary)",
    # admin / Georgia census
    "SETTL_GEO": "Settlement Name (Georgian)",
    "SETTL_ENG": "Settlement Name (English)",
    "MUN_GEO": "Municipality (Georgian)",
    "MUN_ENG": "Municipality (English)",
    "REG_GEO": "Region (Georgian)",
    "REG_ENG": "Region (English)",
    # hydro
    "IDR_ID": "ERICA Catchment ID",
    "R_Basin": "River Basin",
    "GRIDCODE": "Grid Code",
    "code": "Code",
    "Code": "Code",
    "RCode": "River Code",
    "DN": "Digital Number / Class Code",
    "path": "Source Path",
}


def sanitize_alias(label: str, max_len: int = 50) -> str:
    """MapX aliases: max 50 chars; avoid exotic unicode that can fail form validation."""
    if not label:
        return label
    s = (
        label.replace("\u00b2", "2")
        .replace("\u00b3", "3")
        .replace("\u00b0", " deg")
        .replace("\u2192", "->")
        .replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u00e9", "e")
        .replace("\u00e8", "e")
    )
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > max_len:
        s = s[: max_len - 1].rstrip() + "."
    return s


def humanize_field(name: str) -> str:
    if name in FIELD_LABELS:
        return sanitize_alias(FIELD_LABELS[name])
    for k, v in FIELD_LABELS.items():
        if k.lower() == name.lower():
            return sanitize_alias(v)
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    s = s.replace("_", " ").strip()
    label = s[:1].upper() + s[1:] if s else name
    return sanitize_alias(label)

URL_RE = re.compile(r"https?://[^\s\)\]>,\"']+", re.I)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
GEOM_HINTS = {
    "POINT",
    "LINESTRING",
    "POLYGON",
    "MULTIPOINT",
    "MULTILINESTRING",
    "MULTIPOLYGON",
    "GEOMETRY",
    "GEOMETRYCOLLECTION",
}


def empty_i18n(en: str) -> dict:
    return {"en": en, **EMPTY_LANG}


def resolve_gpkg(local_source: str) -> Path | None:
    if not local_source:
        return None
    raw = local_source.replace("/", "\\")
    name = Path(raw).name
    candidates = [
        HERE / "database" / "gpkg" / name,
        HERE / raw,
        HERE.parent / raw,
        HERE / raw.replace("sustainable_caucasus_archive\\", ""),
    ]
    for c in candidates:
        if c.exists() and c.suffix.lower() == ".gpkg":
            return c
    return None


def extract_fields(gpkg: Path) -> tuple[list[dict], str]:
    con = sqlite3.connect(str(gpkg))
    cur = con.cursor()
    tables = cur.execute(
        "SELECT table_name FROM gpkg_contents WHERE data_type='features'"
    ).fetchall()
    if not tables:
        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'gpkg_%' AND name NOT LIKE 'rtree_%' "
            "AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    if not tables:
        con.close()
        return [], ""
    tname = tables[0][0]
    cols = cur.execute(f'PRAGMA table_info("{tname}")').fetchall()
    fields = []
    for _cid, cname, ctype, *_rest in cols:
        ct = (ctype or "").upper()
        if cname.lower() in {"geom", "geometry", "the_geom", "shape"}:
            continue
        if any(g in ct for g in GEOM_HINTS):
            continue
        fields.append({"name": cname, "type": ctype or ""})
    con.close()
    return fields, tname


def polish_abstract(raw: str, title: str, layer_kind: str) -> str:
    if not raw or raw.lower().strip() == "no abstract provided":
        kind = "raster" if layer_kind == "raster" else "vector"
        return (
            f"{title} — {kind} dataset for the Caucasus region, compiled in the "
            f"Sustainable Caucasus GeoNode archive and limited to the ecoregion "
            f"extent where applicable. Intended for environmental assessment, "
            f"spatial planning, and regional decision support."
        )
    text = raw.strip()
    replacements = [
        ("This layers shows", "Dataset showing"),
        ("This layers ", "Dataset covering "),
        ("This layer shows", "Dataset showing"),
        ("This layer has been downloaded from", "Dataset obtained from"),
        ("This layer represents", "Dataset representing"),
        ("Here is the", "Outlines from the"),
        ("Here is ", ""),
        ("Thos original", "The original"),
        ("Th uni is", "The unit is"),
        ("be cropped", "been cropped"),
        ("categoriesand", "categories and"),
        ("teh hydrosheds", "the HydroSHEDS"),
        ("annuak", "annual"),
        ("Azerbaïjian", "Azerbaijan"),
        ("polyon", "polygon"),
        ("Georgiian", "Georgian"),
        ("OpenstreetMAp", "OpenStreetMap"),
        ("OpenstreetMap", "OpenStreetMap"),
        ("  ", " "),
    ]
    for a, b in replacements:
        text = text.replace(a, b)
    text = re.sub(r"\s+", " ", text).strip()
    # Soften remaining weak openings
    if text.lower().startswith("this is a map"):
        text = "Map product" + text[12:]
    if text.lower().startswith("this map "):
        text = "Map product " + text[9:]
    if text.lower().startswith("gis data shows"):
        text = "Spatial dataset showing" + text[14:]
    if text.lower().startswith("gis layer provides"):
        text = "Spatial dataset providing" + text[18:]
    if not text.endswith("."):
        text += "."
    return text


def clean_notes_html(notes: str) -> str:
    return sanitize_alias(notes, max_len=100000).replace("->", "->")  # keep ascii arrow


def notes_from_abstract(abstract: str, title: str, layer_kind: str, years: list[str]) -> str:
    bullets = []
    bullets.append(f"Dataset title: {title}.")
    if years:
        bullets.append(f"Reference year(s) identified from metadata/name: {', '.join(years)}.")
    if "clip" in abstract.lower() or "crop" in abstract.lower() or "extent" in abstract.lower():
        bullets.append("Spatial coverage is limited to the Caucasus ecoregion / study area extent.")
    urls = URL_RE.findall(abstract)
    if urls:
        bullets.append("See origin links for the primary data provider.")
    if layer_kind == "raster":
        bullets.append("Raster values represent the thematic variable described in the abstract.")
    else:
        bullets.append("Attribute definitions follow the source GeoPackage schema.")
    bullets.append(
        "Bounding box is an approximate Caucasus extent; use MapX Update values from source for precision."
    )
    bullets.append("Please verify licensing and citation with the original data provider before redistribution.")
    lis = "".join(f"<li>{sanitize_alias(b, 200)}</li>" for b in bullets)
    return f"<ul>{lis}</ul>"


def extract_urls(text: str) -> list[dict]:
    found = []
    seen = set()
    for u in URL_RE.findall(text or ""):
        u = u.rstrip(").,;")
        if u in seen:
            continue
        seen.add(u)
        host = urlparse(u).netloc.replace("www.", "")
        found.append(
            {
                "is_download_link": u.lower().endswith((".zip", ".tif", ".gpkg", ".shp", ".gz")),
                "url": u,
                "label": host or u,
            }
        )
    return found


def guess_years(name: str, abstract: str, title: str) -> list[str]:
    years = YEAR_RE.findall(f"{name} {title} {abstract}")
    # YEAR_RE with groups returns tuples - fix pattern usage
    years = re.findall(r"\b((?:19|20)\d{2})\b", f"{name} {title} {abstract}")
    # unique preserve order
    out = []
    for y in years:
        if y not in out:
            out.append(y)
    return out[:4]


def country_m49(name: str, title: str, theme: str) -> list[str]:
    blob = f"{name} {title}".lower()
    mapping = {
        "armenia": ["ARM"],
        "arm_": ["ARM"],
        "azerbaijan": ["AZE"],
        "aze_": ["AZE"],
        "georgia": ["GEO"],
        "geo_": ["GEO"],
        "iran": ["IRN"],
        "irn_": ["IRN"],
        "turkey": ["TUR"],
        "tur_": ["TUR"],
        "russia": ["RUS"],
    }
    hits = []
    for key, codes in mapping.items():
        if key in blob:
            for c in codes:
                if c not in hits:
                    hits.append(c)
    if hits and ("caucasus" not in blob and "ecoregion" not in blob):
        return hits
    return list(CAUCASUS_M49)


def build_keywords(name: str, title: str, theme: str) -> dict:
    keys = [name]
    # Glacier-specific keywords only for glacier layers
    if "glacier" in name.lower() or "glims" in name.lower():
        keys.extend(["glaciers", "cryosphere", "glacier inventory", "hydrology", "water"])
        topics = ["inlandWaters", "geoscientificInformation"]
        gemet = ["2924", "4612"]
    elif "hydroshed" in name.lower() or "river" in name.lower():
        keys.extend(["HydroSHEDS", "rivers", "river network", "hydrology", "freshwater"])
        topics = ["inlandWaters"]
        gemet = ["2924", "7235", "4612"]
    else:
        keys.extend(THEME_KEYS.get(theme, ["caucasus"]))
        topics = THEME_TOPIC.get(theme, ["environment"])
        gemet = THEME_GEMET.get(theme, ["4612"])
    for tok in re.split(r"[^A-Za-z0-9]+", title):
        t = tok.strip().lower()
        if len(t) >= 4 and t not in keys and t not in {"from", "with", "this", "that", "based"}:
            keys.append(t)
        if len(keys) >= 10:
            break
    if "caucasus" not in [k.lower() for k in keys]:
        keys.append("caucasus")
    return {
        "keys": keys[:12],
        "keys_m49": country_m49(name, title, theme),
        "keys_gemet": gemet,
        "keys_topic": topics,
    }


def attribution_from(abstract: str, theme: str, name: str) -> str:
    urls = extract_urls(abstract)
    low = (abstract + " " + name).lower()
    # Caucasus multi-country socio layers: do NOT attribute only to GeoStat
    if any(
        x in name.lower()
        for x in (
            "caucasus_population",
            "caucasus_annual_growth",
            "caucasus_urbanization",
            "total_population",
        )
    ):
        return (
            "National statistical offices of Armenia, Azerbaijan, Georgia, Iran, "
            "Russia and Turkey; compiled in the Sustainable Caucasus archive."
        )
    if name.startswith("pop_") and ("georgia" in low or "geostat" in low):
        return "GeoStat (Georgia); GIS: GeoGraphic."
    if urls:
        hosts = ", ".join(sorted({u["label"] for u in urls}))
        return (
            f"Original data providers referenced in source metadata: {hosts}. "
            "Sustainable Caucasus / UNEP-GRID compilation."
        )
    if "intact forest" in low or name.startswith("IFL_"):
        return "Intact Forest Landscapes Project, Transparent World, and Global Forest Watch."
    if "protectedplanet" in low or "wdpa" in low or "protect_areas" in name.lower():
        return "UNEP-WCMC and IUCN - World Database on Protected Areas / Protected Planet."
    if "esa" in name.lower() or "esa-landcover" in low:
        return "European Space Agency (ESA) Climate Change Initiative - Land Cover."
    if "ghs" in name.lower() or "ghsl" in low:
        return "European Commission, Joint Research Centre - Global Human Settlement Layer (GHSL)."
    if "hydroshed" in low:
        return "HydroSHEDS (WWF / USGS and partners)."
    return "Sustainable Caucasus GeoNode archive; see original provider links where available."


def citation_from(title: str, abstract: str, years: list[str], urls: list[dict]) -> str:
    year = years[0] if years else "n.d."
    link = urls[0]["url"] if urls else ""
    if link:
        return f"{title} ({year}). Source metadata from the Sustainable Caucasus GeoNode archive. Available via {link}."
    return f"{title} ({year}). Compiled for the Sustainable Caucasus MapX publication from the GeoNode/GeoServer archive."


# MapX UI shows 01.01.0001 when date unknown; JSON uses ISO 0001-01-01
TEMPORAL_UNKNOWN = "0001-01-01"


def temporal_block(years: list[str]) -> dict:
    if not years:
        return {
            "issuance": {
                "periodicity": "notPlanned",
                "released_at": TEMPORAL_UNKNOWN,
                "modified_at": TEMPORAL_UNKNOWN,
            },
            "range": {
                "is_timeless": True,
                "start_at": TEMPORAL_UNKNOWN,
                "end_at": TEMPORAL_UNKNOWN,
            },
        }
    y0 = years[0]
    y1 = years[-1]
    return {
        "issuance": {
            "periodicity": "notPlanned",
            "released_at": f"{y0}-01-01",
            "modified_at": f"{y1}-01-01",
        },
        "range": {
            "is_timeless": False,
            "start_at": f"{y0}-01-01",
            "end_at": f"{y1}-12-31",
        },
    }


def normalize_temporal(temporal: dict) -> dict:
    """Fill empty date strings so MapX paste does not require manual dates."""
    iss = temporal.setdefault("issuance", {})
    rng = temporal.setdefault("range", {})
    for key in ("released_at", "modified_at"):
        if not iss.get(key):
            iss[key] = TEMPORAL_UNKNOWN
    for key in ("start_at", "end_at"):
        if not rng.get(key):
            rng[key] = TEMPORAL_UNKNOWN
    if rng.get("is_timeless") is None and iss.get("released_at") == TEMPORAL_UNKNOWN:
        rng["is_timeless"] = True
    return temporal


def spatial_block(srs: str) -> dict:
    code = (srs or "EPSG:4326").strip()
    epsg = code.split(":")[-1] if ":" in code else code
    return {
        "crs": {
            "code": code if code.startswith("EPSG:") else f"EPSG:{epsg}",
            "url": f"http://spatialreference.org/ref/epsg/{epsg}/",
        },
        "bbox": dict(CAUCASUS_BBOX),
    }


def attributes_block(fields: list[dict]) -> dict:
    attrs = {}
    for f in fields:
        # skip pure internal ids if many fields? keep all non-geom for fidelity
        label = empty_i18n(humanize_field(f["name"]))
        attrs[f["name"]] = label
    return attrs


def homepage_from(urls: list[dict]) -> dict:
    if not urls:
        return {"url": ""}
    # prefer non-download
    for u in urls:
        if not u["is_download_link"]:
            return {"url": u["url"]}
    return {"url": urls[0]["url"]}


def load_overrides() -> dict:
    if OVERRIDES.exists():
        return json.loads(OVERRIDES.read_text(encoding="utf-8"))
    return {}


def build_one(row: dict, char: dict, fields: list[dict], overrides: dict) -> dict:
    name = row["geonode_name"]
    title = (row.get("title") or row.get("geonode_title") or name).strip()
    theme = row.get("theme") or "other"
    kind = row.get("layer_kind") or "vector"
    abstract_raw = (char.get("abstract") or "").strip()
    ov = overrides.get(name, {})

    title_en = ov.get("title") or title
    abstract_en = ov.get("abstract") or polish_abstract(abstract_raw, title_en, kind)
    years = guess_years(name, abstract_raw + " " + abstract_en, title_en)
    if ov.get("years"):
        years = list(ov["years"])
    urls = extract_urls(abstract_raw)
    if ov.get("source_urls"):
        urls = ov["source_urls"]

    notes_en = ov.get("notes") or notes_from_abstract(abstract_en, title_en, kind, years)
    notes_en = (
        notes_en.replace("\u2192", "->")
        .replace("\u00b2", "2")
        .replace("\u2014", "-")
        .replace("\u2013", "-")
    )
    attribution = ov.get("data_attribution") or attribution_from(abstract_raw, theme, name)
    attribution = attribution.replace("\u2014", "-").replace("\u2013", "-")
    citation = ov.get("citation") or citation_from(title_en, abstract_en, years, urls)
    attrs = attributes_block(fields) if kind == "vector" else {}
    # Re-sanitize all attribute labels
    for k, v in attrs.items():
        v["en"] = sanitize_alias(v.get("en") or k)
    keywords = build_keywords(name, title_en, theme)
    if ov.get("keywords"):
        keywords = ov["keywords"]
    elif name == "caucasus_glaciers":
        keywords = {
            "keys": [
                "caucasus_glaciers",
                "Randolph Glacier Inventory",
                "RGI 6.0",
                "glaciers",
                "cryosphere",
                "ASTER",
                "glacier inventory",
                "caucasus",
            ],
            "keys_m49": list(CAUCASUS_M49),
            "keys_gemet": ["2924", "4612"],
            "keys_topic": ["inlandWaters", "geoscientificInformation"],
        }
    elif name == "hydroshed_main_rivers_Caucasus":
        keywords = {
            "keys": [
                "hydroshed_main_rivers_Caucasus",
                "HydroSHEDS",
                "rivers",
                "river network",
                "hydrology",
                "freshwater",
                "drainage",
                "caucasus",
            ],
            "keys_m49": list(CAUCASUS_M49),
            "keys_gemet": ["2924", "7235", "4612"],
            "keys_topic": ["inlandWaters"],
        }

    temporal = ov.get("temporal") or temporal_block(years)
    # Force safe periodicity enum value
    if temporal.get("issuance", {}).get("periodicity") not in {
        "notPlanned",
        "asNeeded",
        "irregular",
        "annual",
        "monthly",
        "daily",
        "weekly",
        "quarterly",
        "continual",
        "unknown",
    }:
        temporal.setdefault("issuance", {})["periodicity"] = "notPlanned"
    # Prefer notPlanned unless override set years with explicit temporal
    if not ov.get("temporal"):
        temporal["issuance"]["periodicity"] = "notPlanned"
    temporal = normalize_temporal(temporal)

    license_text = ov.get("license_text") or (
        "Please refer to the original data provider's terms of use and licensing "
        "conditions. See origin links when available."
    )
    license_name = ov.get("license_name") or "Provider terms"

    homepage = homepage_from(urls)
    if not homepage.get("url"):
        homepage = {"url": "https://www.mapx.org"}

    meta = {
        "text": {
            "title": empty_i18n(title_en),
            "abstract": empty_i18n(abstract_en),
            "keywords": keywords,
            "attributes": attrs,
            "attributes_alias": json.loads(json.dumps(attrs)),
            "notes": empty_i18n(notes_en),
            "language": {"codes": [{"code": "en"}]},
            "data_attribution": attribution,
            "citation": citation,
        },
        "temporal": temporal,
        "spatial": spatial_block(row.get("srs") or "EPSG:4326"),
        "contact": {"contacts": [dict(DEFAULT_CONTACT)]},
        "origin": {
            "homepage": homepage,
            "source": {"urls": urls},
        },
        "license": {
            "licenses": [
                {
                    "name": license_name,
                    "text": license_text,
                }
            ]
        },
        "annex": {"references": []},
    }
    return meta


def build_inventory(pub: list[dict], char_by: dict) -> list[dict]:
    out = []
    for r in pub:
        ab = (char_by.get(r["geonode_name"], {}).get("abstract") or "").strip()
        out.append(
            {
                "geonode_name": r["geonode_name"],
                "mapx_id": (r.get("mapx_id") or "").strip(),
                "mapx_url_status": (r.get("mapx_url_status") or "").strip(),
                "layer_kind": r["layer_kind"],
                "title": r.get("title") or "",
                "geonode_title": r.get("geonode_title") or "",
                "srs": r.get("srs") or "",
                "theme": r.get("theme") or "",
                "local_source": r.get("local_source") or "",
                "catalog_notes": r.get("notes") or "",
                "abstract_raw": ab,
                "abstract_ok": bool(ab and ab.lower() != "no abstract provided"),
            }
        )
    return out


def extract_all_schemas(pub: list[dict]) -> dict:
    schemas = {}
    for r in pub:
        name = r["geonode_name"]
        if r["layer_kind"] != "vector":
            schemas[name] = {"fields": [], "kind": "raster"}
            continue
        gpkg = resolve_gpkg(r.get("local_source") or "")
        if not gpkg:
            schemas[name] = {"fields": [], "kind": "vector", "error": "gpkg_missing"}
            continue
        try:
            fields, table = extract_fields(gpkg)
            schemas[name] = {
                "fields": fields,
                "kind": "vector",
                "table": table,
                "path": str(gpkg),
            }
        except Exception as exc:  # noqa: BLE001
            schemas[name] = {
                "fields": [],
                "kind": "vector",
                "error": str(exc),
                "path": str(gpkg),
            }
    return schemas


def status_for(row: dict, abstract_ok: bool) -> str:
    if (row.get("mapx_url_status") or "") == "wrong_layer":
        return "wrong_layer_warn"
    if not (row.get("mapx_id") or "").strip():
        return "no_mapx_id"
    if not abstract_ok:
        return "needs_review"
    return "ready"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pub = [
        r
        for r in csv.DictReader(CATALOG.open(encoding="utf-8-sig"))
        if (r.get("publish") or "") == "yes"
    ]
    char_by = {
        r["name"]: r for r in csv.DictReader(CHAR.open(encoding="utf-8-sig"))
    }
    overrides = load_overrides()

    inventory = build_inventory(pub, char_by)
    (OUT_DIR / "_inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    schemas = extract_all_schemas(pub)
    (OUT_DIR / "_schemas.json").write_text(
        json.dumps(schemas, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    index_rows = []
    for r in pub:
        name = r["geonode_name"]
        char = char_by.get(name, {})
        fields = schemas.get(name, {}).get("fields") or []
        meta = build_one(r, char, fields, overrides)
        out_path = OUT_DIR / f"{name}.json"
        out_path.write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        urls = meta["origin"]["source"]["urls"]
        abstract_ok = bool(
            (char.get("abstract") or "").strip()
            and (char.get("abstract") or "").strip().lower() != "no abstract provided"
        )
        st = status_for(r, abstract_ok)
        index_rows.append(
            {
                "geonode_name": name,
                "mapx_id": (r.get("mapx_id") or "").strip(),
                "mapx_url_status": (r.get("mapx_url_status") or "").strip(),
                "layer_kind": r["layer_kind"],
                "theme": r.get("theme") or "",
                "n_attributes": len(fields),
                "status": st,
                "source_urls_found": ";".join(u["url"] for u in urls),
                "output_json": str(out_path.relative_to(HERE.parent)).replace("/", "\\")
                if False
                else f"sustainable_caucasus_archive\\mapx_metadata\\{name}.json",
                "notes": (r.get("notes") or "").strip(),
            }
        )

    # write index
    idx_path = OUT_DIR / "_metadata_index.csv"
    with idx_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "geonode_name",
                "mapx_id",
                "mapx_url_status",
                "layer_kind",
                "theme",
                "n_attributes",
                "status",
                "source_urls_found",
                "output_json",
                "notes",
            ],
        )
        w.writeheader()
        w.writerows(index_rows)

    # QA notes
    no_mapx = [r for r in index_rows if r["status"] == "no_mapx_id"]
    wrong = [r for r in index_rows if r["status"] == "wrong_layer_warn"]
    needs = [r for r in index_rows if r["status"] == "needs_review"]
    schema_err = [n for n, s in schemas.items() if s.get("error")]

    qa = []
    qa.append("# MapX metadata QA notes\n")
    qa.append(f"- Total JSON written: **{len(index_rows)}**\n")
    qa.append(f"- ready: {sum(1 for r in index_rows if r['status']=='ready')}\n")
    qa.append(f"- no_mapx_id: {len(no_mapx)}\n")
    qa.append(f"- wrong_layer_warn: {len(wrong)}\n")
    qa.append(f"- needs_review: {len(needs)}\n")
    qa.append("\n## wrong_layer (do not paste into wrong MapX view)\n")
    for r in wrong:
        qa.append(f"- `{r['geonode_name']}` → catalog mapx_id `{r['mapx_id']}` ({r['notes']})\n")
    qa.append("\n## no_mapx_id\n")
    for r in no_mapx:
        qa.append(f"- `{r['geonode_name']}` ({r['layer_kind']})\n")
    qa.append("\n## needs_review (weak/missing GeoNode abstract)\n")
    for r in needs:
        qa.append(f"- `{r['geonode_name']}`\n")
    if schema_err:
        qa.append("\n## GPKG schema errors\n")
        for n in schema_err:
            qa.append(f"- `{n}`: {schemas[n].get('error')}\n")
    qa.append(
        "\n## ID integrity\n"
        "- Every `mapx_id` in `_metadata_index.csv` is copied verbatim from "
        "`triage/publication_catalog.csv` for the same `geonode_name`.\n"
        "- No MX- identifiers were invented.\n"
    )
    (OUT_DIR / "_qa_notes.md").write_text("".join(qa), encoding="utf-8")

    print(f"Wrote {len(index_rows)} metadata JSON -> {OUT_DIR}")
    print(
        "status",
        {
            s: sum(1 for r in index_rows if r["status"] == s)
            for s in sorted({r["status"] for r in index_rows})
        },
    )
    if schema_err:
        print("schema_errors", schema_err)


if __name__ == "__main__":
    main()
