#!/usr/bin/env python3
"""Score GeoServer layers for a curated MapX catalogue.

Reads geoserver_layers_all_workspaces.csv and style_manifest.csv, then writes:

- layer_characterization.csv
- duplicate_families.csv
- source_availability.csv
- characterization_summary.txt

Scoring follows the Sustainable Caucasus (SCAC) triage plan:
technical quality (0-40) + thematic relevance (0-45), scaled to 0-100.
Duplicate families, GeoServer demos, MODIS daily scenes and out-of-region
layers are forced to P4 regardless of score.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
LAYERS_CSV = HERE / "geoserver" / "geoserver" / "geoserver_layers_all_workspaces.csv"
STYLES_CSV = HERE / "geoserver" / "geoserver" / "style_manifest.csv"
ARCHIVE_ROOT = HERE
GEONODE_MAPX_ROOT = HERE.parent

CAUCASUS_LATLON = (36.0, 48.0, 36.0, 54.0)  # minlat, maxlat, minlon, maxlon

HASH_RE = re.compile(r"_[0-9a-f]{8,}$", re.I)
UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.I,
)
MODIS_RE = re.compile(
    r"(caucasus|azerbaijan)_2017(232|233|234|235|236)_(aqua|terra)(_721)?_250m$",
    re.I,
)

# Explicit keepers when several GeoNode imports represent the same dataset.
FAMILY_KEEPERS = {
    "aze_roads": "aze_roads",
    "geo_roads": "geo_roads",
    "irn_roads": "irn_roads",
    "tur_roads": "tur_roads",
    "wdpa_caucasus": "WDPA_Caucasus",
    "caucasus_ecocorridors": "Caucasus_Ecocorridors_WGS84",
    "priority_conservation_areas": "Priority_Conservation_Areas_WGS84",
    "mountains_delimitations_geom": "mountains_delimitations_caucasus_clip0",
    "elevation_caucasus": "elevation_caucasus",
    "forest_height_2019": "Forest_height_2019_NAFR_Caucasus_Ecoregion",
    "caucasus_population_density_2020": "caucasus_population_density_2020",
    "centre_of_regions": "Centre_of_regions",
    "gdp_composition": "gdp_composition",
    "nuts3_hectares": "nuts3_2000_2020hectares_last",
    "k2_gmba_vector": "K2_v2_0_2022_07_Caucasus1",
    "seismic_hazard_armenia_raster": "seismic_hazard_armenia",
    "hydrogeology_armenia": "Hydrogeology",
    "ifl_2013": "IFL_2013_Caucasus",
}

# Core SCAC layers that should go to MapX first (plan P1 list).
EXPLICIT_P1 = {
    "ESA2000_Cauc",
    "ESA2005_Cauc",
    "ESA2010_Cauc",
    "elevation_caucasus",
    "k1_kapos",
    "k2_gmba_thermal",
    "k3_elu_lf",
    "k1k2k3_matrix",
    "gmba_thermal",
    "Forest_height_2019_NAFR_Caucasus_Ecoregion",
    "ls_risk_cauc",
    "GHS_2015",
    "caucasus_ecoregion_wgs84_new",
    "mountains_delimitations_caucasus_clip0",
    "mountains_delimitations_caucasus_etiquettes",
    "WDPA_Caucasus",
    "Caucasus_Ecocorridors_WGS84",
    "Priority_Conservation_Areas_WGS84",
    "emerald_2020_epsg4326_caucasus",
    "caucasus_glaciers",
    "leopard_distribution_area_wgs84",
    "IFL_2000_Caucasus",
    "IFL_2013_Caucasus",
    "IFL_difference_2000_2013_Caucasus",
    "protect_areas",
    "hydroshed_main_rivers_Caucasus",
    "roads_caucasus_select",
    "railroads",
    "caucasus_population_density_2020",
    "caucasus_urbanization_level_2020a",
    "caucasus_annual_growth_pop_2020a",
    "total_population_2019_NUTS2",
    "UNESCO_WHC_sites_Caucasus_geonode",
    "fires_2020",
    "caucasus_ecoregion_forest_cover",
    "caucasus_ecoregion_land_cover",
}

# National unique / supporting products — publish after P1.
EXPLICIT_P2 = {
    "co2_2010",
    "biomes_caucasus_clip",
    "seismic_hazard_armenia",
    "tree_cover",
    "dem_200_000",
    "thickness_rgi_12_2021july09",
    "v_rgi_12_2021july01",
    "rgi_caucasus",
    "glims_polygons",
    "arm_catchmets",
    "arm_rivers_erica",
    "arm_forest_area",
    "arm_landuse",
    "armenia_landslide",
    "armenia_prec",
    "avalanches",
    "climat",
    "flooding_duration",
    "flooding_layer",
    "mudflow_arm",
    "model_2017",
    "seismic_zones",
    "seismic_model_causin_2005",
    "soil_arm",
    "temperature",
    "vegetation_arm",
    "landscape",
    "lakes_and_reservoirs",
    "Hydrogeology",
    "Groundwater_zones",
    "springs0",
    "wind_resources",
    "GE_avalanches",
    "GE_coastal_erosion",
    "GE_floods",
    "GE_hazards",
    "GE_mudflows",
    "geo_catchment",
    "geo_rivers_erica",
    "georgia_land_cover_wgs84",
    "georgia_soils_new",
    "pa",
    "geo_roads",
    "aze_roads",
    "administrative_regions_of_azerbaijan",
    "_1",
    "the_landscape_map_of_azerbaijan_1",
    "river_of_azerbaijan_republic_1",
    "reservoirs_of_azerbaijan_republic_2",
    "water_channels_in_azerbaijan",
    "main_types_of_climate_1",
    "sc_rivers",
    "all_rivers_by_basin",
    "GWSP_Caucasus",
    "heritage_UNESCO_2021_caucasus_clip",
    "caucasus_pois_clip_culture",
    "health_facilities",
    "educ_facilities",
    "pop_1989",
    "pop_2002",
    "pop_2014",
    "forest_fires_2005_wgs84",
    "forest_fires_2010",
    "forest_zones",
    "gdp_per_capita",
    "gdp_composition",
    "K2_v2_0_2022_07_Caucasus1",
    "caucasus_air_quality_stations_clipped",
    "solar_radiation",
    "radiance_duration",
    "radiation_bal",
}

DEMO_OR_OUT = {
    "tasmania_water_bodies",
    "ve",
    "ProvCM01012019_g_WGS84_lKHiGZ3",
}

OSM_EXTRA_COUNTRY = {"irn_roads", "irn_roads_1", "tur_roads", "tur_roads_1"}

CITY_DRAFTS = {"City0", "City1", "City2", "City3"}

SUBNATIONAL = {
    "The_mountainous_Shirvan0",
    "The_Mountainous_Shirvan",
    "The_Shaki_Zagatala_Economic_Geographic_Region",
    "Kalbajar_Lachin_economical_geographic_region",
    "Yukari_Karabagh_economic_geographic_region",
    "Centre_of_regions",
    "kolkheti_habitats",
    "kolkheti_lakes",
    "kolkheti_rivers",
    "kolkheti_settlements",
}


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def blob(row: dict) -> str:
    return " ".join(
        [
            row.get("name") or "",
            row.get("title") or "",
            row.get("keywords") or "",
            row.get("abstract") or "",
        ]
    ).lower()


def parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def bbox_intersects_caucasus(row: dict) -> bool:
    minx = parse_float(row.get("latlon_bbox_minx"))
    miny = parse_float(row.get("latlon_bbox_miny"))
    maxx = parse_float(row.get("latlon_bbox_maxx"))
    maxy = parse_float(row.get("latlon_bbox_maxy"))
    if None in (minx, miny, maxx, maxy):
        return False
    lat_min, lat_max, lon_min, lon_max = CAUCASUS_LATLON
    return not (maxy < lat_min or miny > lat_max or maxx < lon_min or minx > lon_max)


def abstract_ok(row: dict) -> bool:
    text = (row.get("abstract") or "").strip()
    if not text:
        return False
    if text.lower() in {"no abstract provided", "generated from geotiff"}:
        return False
    return len(text) >= 20


def title_ok(row: dict) -> bool:
    title = (row.get("title") or "").strip()
    name = (row.get("name") or "").strip()
    if not title:
        return False
    return title.lower() != name.lower()


def keywords_thematic(row: dict) -> bool:
    kw = (row.get("keywords") or "").strip()
    if not kw:
        return False
    name = (row.get("name") or "").lower()
    tokens = [t.strip().lower() for t in kw.split(";") if t.strip()]
    useful = [
        t
        for t in tokens
        if t not in {"features", "geotiff", "wcs", name, name.replace("_", " ")}
    ]
    return len(useful) >= 1


def country_scope(row: dict) -> str:
    name = (row.get("name") or "").lower()
    title = (row.get("title") or "").lower()
    text = f"{name} {title}"
    if name in {n.lower() for n in DEMO_OR_OUT} or "tasmania" in name or "provcm" in name:
        return "out_of_region"
    if name in {n.lower() for n in OSM_EXTRA_COUNTRY}:
        return "extra_country"
    tags = []
    if re.search(r"armenia|\barm_|_arm\b", text):
        tags.append("ARM")
    if re.search(
        r"azerbaijan|\baze_|shaki|shirvan|karabagh|kalbajar|zagatala", text
    ):
        tags.append("AZE")
    if re.search(
        r"georgia|\bgeo_|kolkheti|\bge_flood|\bge_hazard|\bge_aval|\bge_mud|\bge_coast",
        text,
    ):
        tags.append("GEO")
    if re.search(
        r"caucasus|ecoregion|wdpa|emerald|glims|rgi_|kapos|gmba|hydroshed|ghs_|\bnuts",
        text,
    ):
        tags.append("REGIONAL")
    if "REGIONAL" in tags:
        return "regional"
    if len(set(tags) & {"ARM", "AZE", "GEO"}) == 1:
        return "national"
    if tags:
        return "national"
    return "other"


def theme(row: dict) -> str:
    text = blob(row)
    rules = [
        ("imagery_modis_s2", r"2017(232|233|234|235|236)|s2_2017|_20170823"),
        ("elevation_mountains", r"\bdem_|elevation|wc2.?1.*elev|kapos|gmba|\bk1_|\bk2_|\bk3_|k1k2k3|mountain"),
        ("land_cover", r"land.?cover|landuse|esa20|glc30|2000lc|2010lc|biomes"),
        ("forest", r"forest|tree_cover|\bifl\b|intact"),
        ("biodiversity_pa", r"wdpa|protect|emerald|ecocorridor|conservation|leopard|\bpa\b"),
        ("hazard", r"seismic|landslide|ls_risk|avalanche|flood|mudflow|hazard|fire|coastal"),
        ("climate", r"precip|climat|temperat|solar|radiat|wind|\bco2\b"),
        ("population_socio", r"population|\bpop_|urban|gdp|\bnuts|educ|health|\bcity|settlement"),
        ("water_glacier", r"river|catchm|lake|reservoir|hydro|spring|glacier|\brgi\b|glims|water|runoff|channel|\bdam"),
        ("admin_boundaries", r"admin|economic.?geograph|boundary|centre_of"),
        ("infrastructure", r"road|rail"),
        ("culture_tourism", r"unesco|poi|tourism|culture|heritage"),
    ]
    for label, pattern in rules:
        if re.search(pattern, text, re.I):
            return label
    return "other"


def scale_points(scope: str, row: dict) -> int:
    text = blob(row)
    if scope == "regional":
        return 12
    if re.search(r"shirvan|shaki|kolkheti|kalbajar|karabagh|zagatala", text):
        return 4
    if scope == "national":
        return 8
    if scope == "extra_country":
        return 2
    return 0


def core_theme_points(theme_name: str) -> int:
    if theme_name in {
        "elevation_mountains",
        "land_cover",
        "forest",
        "biodiversity_pa",
        "hazard",
        "water_glacier",
        "population_socio",
    }:
        return 10
    if theme_name in {"climate", "admin_boundaries", "infrastructure"}:
        return 5
    if theme_name == "culture_tourism":
        return 4
    return 0


def timeseries_points(row: dict) -> int:
    name = row.get("name") or ""
    if name in {
        "ESA2000_Cauc",
        "ESA2005_Cauc",
        "ESA2010_Cauc",
        "IFL_2000_Caucasus",
        "IFL_2013_Caucasus",
        "IFL_difference_2000_2013_Caucasus",
        "pop_1989",
        "pop_2002",
        "pop_2014",
        "forest_fires_2005_wgs84",
        "forest_fires_2010",
        "caucasus_population_density_2020",
        "GHS_2015",
    }:
        return 8
    return 0


def cited_product_points(row: dict) -> int:
    text = blob(row)
    if re.search(
        r"wdpa|esa|srtm|ghs|rgi|emerald|ifl|glims|kapos|gmba|hydroshed|worldclim|glc30|erica|ecrins|unesco",
        text,
    ):
        return 8
    return 0


def base_layer_points(row: dict) -> int:
    name = row.get("name") or ""
    if name in {
        "caucasus_ecoregion_wgs84_new",
        "mountains_delimitations_caucasus_clip0",
        "mountains_delimitations_caucasus_etiquettes",
        "elevation_caucasus",
        "hydroshed_main_rivers_Caucasus",
        "roads_caucasus_select",
        "WDPA_Caucasus",
        "k1k2k3_matrix",
        "railroads",
    }:
        return 7
    return 0


def crs_points(srs: str) -> int:
    if srs == "EPSG:4326":
        return 4
    if srs in {"EPSG:32637", "EPSG:32638", "EPSG:32639"}:
        return 2
    return 0


def score_technical(row: dict, style_used: bool) -> int:
    score = 0
    if (row.get("advertised") or "") == "True":
        score += 8
    if title_ok(row):
        score += 6
    if abstract_ok(row):
        score += 8
    if keywords_thematic(row):
        score += 4
    score += crs_points(row.get("srs") or "")
    if style_used:
        score += 4
    if bbox_intersects_caucasus(row):
        score += 6
    return score


def score_relevance(row: dict, theme_name: str, scope: str) -> int:
    return (
        scale_points(scope, row)
        + core_theme_points(theme_name)
        + timeseries_points(row)
        + cited_product_points(row)
        + base_layer_points(row)
    )


def family_for(name: str) -> str | None:
    if name in {"aze_roads", "aze_roads_1"}:
        return "aze_roads"
    if name in {"geo_roads", "geo_roads_1"}:
        return "geo_roads"
    if name in {"irn_roads", "irn_roads_1"}:
        return "irn_roads"
    if name in {"tur_roads", "tur_roads_1"}:
        return "tur_roads"
    if name.lower() == "wdpa_caucasus":
        return "wdpa_caucasus"
    if name.lower() == "caucasus_ecocorridors_wgs84":
        return "caucasus_ecocorridors"
    if name.lower() == "priority_conservation_areas_wgs84":
        return "priority_conservation_areas"
    if name in {
        "mountains_delimitations_caucasus_clip",
        "mountains_delimitations_caucasus_clip0",
        "mountains_delimitations_caucasus_clip1",
    }:
        return "mountains_delimitations_geom"
    if name in {"elevation_caucasus", "elevation_caucasus0"}:
        return "elevation_caucasus"
    if name in {
        "Forest_height_2019_NAFR_Caucasus_Ecoregion",
        "Forest_height_2019_NAFR_Caucasus_Ecoregion0",
    }:
        return "forest_height_2019"
    if name in {
        "caucasus_population_density_2020",
        "caucasus_population_density_20200",
    }:
        return "caucasus_population_density_2020"
    if name in {"Centre_of_regions", "Centre_of_regions0"}:
        return "centre_of_regions"
    if name.startswith("gdp_composition"):
        return "gdp_composition"
    if name.startswith("nuts3_2000_2020hectares_last"):
        return "nuts3_hectares"
    if name.lower().replace(".", "_").startswith("k2_v2"):
        return "k2_gmba_vector"
    if name in {"seismic_hazard_475", "seismic_hazard_armenia"}:
        return "seismic_hazard_armenia_raster"
    if name in {"Hydrogeology", "Hydrogeol_poly0"}:
        return "hydrogeology_armenia"
    if name in {"IFL_2013_Caucasus", "intact_forest_2013"}:
        return "ifl_2013"
    if name in CITY_DRAFTS:
        return "city_points"
    return None


def is_modis(name: str) -> bool:
    return bool(MODIS_RE.match(name))


def is_import_duplicate_name(name: str) -> bool:
    if name in {"_1", "springs0"}:
        return False
    if name in CITY_DRAFTS:
        return True
    if name.endswith("_1"):
        return True
    if HASH_RE.search(name):
        return True
    if UUID_RE.search(name):
        return True
    return False


def mapx_action(tier: str, reasons: list[str]) -> str:
    if "demo_or_out_of_region" in reasons:
        return "drop_demo"
    if tier in {"P1", "P2"}:
        return "publish"
    if tier == "P3":
        return "review"
    return "archive"


def assign_tier(row: dict, score_total: int, reasons: list[str]) -> str:
    name = row.get("name") or ""
    p4_reasons = {
        "demo_or_out_of_region",
        "modis_daily_scene",
        "sentinel2_snapshot",
        "osm_extra_country",
        "city_import_draft",
        "duplicate_not_keeper",
        "local_subnational_raster",
        "archive_unpublished",
        "archive_reimport",
    }
    if p4_reasons & set(reasons):
        return "P4"
    if name in EXPLICIT_P1:
        return "P1"
    if name in SUBNATIONAL:
        return "P3"
    if name in EXPLICIT_P2:
        return "P2"
    if score_total >= 50:
        return "P2"
    if score_total >= 35:
        return "P3"
    return "P4"


def exclusion_reasons(row: dict, family: str | None) -> list[str]:
    name = row.get("name") or ""
    reasons: list[str] = []
    if name in DEMO_OR_OUT:
        reasons.append("demo_or_out_of_region")
    if is_modis(name):
        reasons.append("modis_daily_scene")
    if name in {"s2_20170823"}:
        reasons.append("sentinel2_snapshot")
    if name in OSM_EXTRA_COUNTRY:
        reasons.append("osm_extra_country")
    if name in CITY_DRAFTS:
        reasons.append("city_import_draft")
    if name == "The_Mountainous_Shirvan":
        reasons.append("local_subnational_raster")
    if family and FAMILY_KEEPERS.get(family) not in {None, name}:
        if family != "city_points":
            reasons.append("duplicate_not_keeper")
    if family == "city_points":
        reasons.append("duplicate_not_keeper")
    if is_import_duplicate_name(name) and name not in EXPLICIT_P1 | EXPLICIT_P2:
        if "duplicate_not_keeper" not in reasons:
            reasons.append("geonode_reimport_name")
    if (row.get("advertised") or "") != "True" and name not in EXPLICIT_P1:
        reasons.append("not_advertised")
    return reasons


def styles_by_layer(style_rows: list[dict]) -> dict[str, list[str]]:
    used: dict[str, list[str]] = defaultdict(list)
    for style in style_rows:
        if (style.get("referenced_by_layer") or "").lower() != "yes":
            continue
        layers = style.get("layers") or ""
        for item in layers.split(";"):
            item = item.strip()
            if not item:
                continue
            short = item.split(":")[-1]
            used[short].append(style.get("style_name") or "")
    return used


def normalize_stem(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def find_source_files() -> dict[str, list[Path]]:
    """Index raster/vector files in the local archive by normalized stem."""
    index: dict[str, list[Path]] = defaultdict(list)
    patterns = ("*.gpkg", "*.tif", "*.tiff", "*.geotiff", "*.shp", "*.sql.gz")
    skip_parts = {"styles", "style_metadata", "geoserver_layers"}
    seen: set[Path] = set()
    if not ARCHIVE_ROOT.exists():
        return index
    for pattern in patterns:
        for path in ARCHIVE_ROOT.rglob(pattern):
            if any(part in skip_parts for part in path.parts):
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            index[normalize_stem(path.stem)].append(path)
            index[normalize_stem(path.parent.name)].append(path)
    return index


def relpath(path: Path) -> str:
    try:
        return str(path.relative_to(GEONODE_MAPX_ROOT))
    except ValueError:
        return str(path)


def source_status(row: dict, file_index: dict[str, list[Path]]) -> tuple[str, str]:
    keys = [
        row.get("name") or "",
        row.get("native_name") or "",
        row.get("postgres_table") or "",
        (row.get("name") or "").replace(".", "_"),
        (row.get("name") or "").replace("_", "."),
    ]
    hits: list[Path] = []
    seen: set[Path] = set()
    for key in keys:
        for path in file_index.get(normalize_stem(key), []):
            if path not in seen:
                seen.add(path)
                hits.append(path)
    kind = row.get("layer_kind")
    if hits:
        return "found", "; ".join(relpath(p) for p in hits[:5])
    if kind == "vector":
        return "missing_gpkg", "PostGIS table expected; no GeoPackage in local archive"
    return "missing_geotiff", "GeoTIFF expected; no raster file in local archive"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not LAYERS_CSV.exists():
        raise SystemExit(f"Missing layers CSV: {LAYERS_CSV}")
    if not STYLES_CSV.exists():
        raise SystemExit(f"Missing styles CSV: {STYLES_CSV}")

    layers = load_csv(LAYERS_CSV)
    styles = load_csv(STYLES_CSV)
    style_map = styles_by_layer(styles)
    file_index = find_source_files()

    families: dict[str, list[str]] = defaultdict(list)
    records: list[dict] = []

    for row in layers:
        name = row.get("name") or ""
        family = family_for(name)
        if family:
            families[family].append(name)
        theme_name = theme(row)
        scope = country_scope(row)
        used_styles = style_map.get(name, [])
        style_used = bool(used_styles) or bool(row.get("default_style_name"))
        tech = score_technical(row, style_used)
        rel = score_relevance(row, theme_name, scope)
        total = round((tech + rel) / 85 * 100)
        reasons = exclusion_reasons(row, family)
        # not_advertised alone should not override P2 national keepers
        if "not_advertised" in reasons and name not in EXPLICIT_P1 | EXPLICIT_P2:
            if "duplicate_not_keeper" not in reasons:
                reasons.append("archive_unpublished")
        if "geonode_reimport_name" in reasons and name not in EXPLICIT_P1 | EXPLICIT_P2:
            reasons.append("archive_reimport")
        tier = assign_tier(row, total, reasons)
        if family and FAMILY_KEEPERS.get(family) == name and name in EXPLICIT_P1:
            tier = "P1"
        action = mapx_action(tier, reasons)
        src_status, src_note = source_status(row, file_index)
        notes = []
        if family:
            keeper = FAMILY_KEEPERS.get(family, "")
            if keeper and keeper != name:
                notes.append(f"duplicate of {keeper}")
            elif keeper == name:
                notes.append(f"keeper of family {family}")
        if is_modis(name):
            notes.append("MODIS Aqua/Terra daily scene 2017 DOY 232-236; archive only")
        if name in DEMO_OR_OUT:
            notes.append("demo or outside Caucasus bbox/theme")
        if name == "_1":
            notes.append("opaque GeoNode name; title is Azerbaijan economic zones")
        if (row.get("srs") or "") in {"EPSG:28408", "EPSG:3035", "EPSG:32632"}:
            notes.append(f"reproject {row.get('srs')} to EPSG:4326 before MapX")
        records.append(
            {
                "name": name,
                "qualified_name": row.get("qualified_name") or "",
                "layer_kind": row.get("layer_kind") or "",
                "title": row.get("title") or "",
                "geometry_or_format": row.get("geometry_type")
                or row.get("native_format")
                or ("GeoTIFF" if row.get("layer_kind") == "raster" else ""),
                "srs": row.get("srs") or "",
                "advertised": row.get("advertised") or "",
                "abstract_ok": "yes" if abstract_ok(row) else "no",
                "title_ok": "yes" if title_ok(row) else "no",
                "duplicate_family": family or "",
                "is_family_keeper": "yes"
                if family and FAMILY_KEEPERS.get(family) == name
                else ("no" if family else ""),
                "theme": theme_name,
                "country_scope": scope,
                "style_used": "yes" if style_used else "no",
                "default_style": row.get("default_style_name") or "",
                "score_tech": tech,
                "score_relevance": rel,
                "score_total": total,
                "tier": tier,
                "mapx_action": action,
                "source_status": src_status,
                "source_note": src_note,
                "postgres_table": row.get("postgres_table") or "",
                "store_type": row.get("store_type") or "",
                "notes": "; ".join(notes + reasons),
                "keywords": row.get("keywords") or "",
                "abstract": (row.get("abstract") or "").replace("\n", " ").strip(),
            }
        )

    records.sort(key=lambda r: (r["tier"], -int(r["score_total"]), r["layer_kind"], r["name"]))

    char_fields = [
        "name",
        "qualified_name",
        "layer_kind",
        "title",
        "geometry_or_format",
        "srs",
        "advertised",
        "abstract_ok",
        "title_ok",
        "duplicate_family",
        "is_family_keeper",
        "theme",
        "country_scope",
        "style_used",
        "default_style",
        "score_tech",
        "score_relevance",
        "score_total",
        "tier",
        "mapx_action",
        "source_status",
        "source_note",
        "postgres_table",
        "store_type",
        "notes",
        "keywords",
        "abstract",
    ]
    write_csv(HERE / "layer_characterization.csv", records, char_fields)

    family_rows = []
    for family, names in sorted(families.items()):
        keeper = FAMILY_KEEPERS.get(family, "")
        members = []
        for member in names:
            rec = next(r for r in records if r["name"] == member)
            members.append(
                {
                    "name": member,
                    "tier": rec["tier"],
                    "score_total": rec["score_total"],
                    "advertised": rec["advertised"],
                    "title": rec["title"],
                }
            )
        family_rows.append(
            {
                "family": family,
                "keeper": keeper,
                "n_members": len(names),
                "members": " | ".join(names),
                "mapx_keep": keeper,
                "mapx_archive": " | ".join(n for n in names if n != keeper),
                "member_detail": json.dumps(members, ensure_ascii=False),
            }
        )
    write_csv(
        HERE / "duplicate_families.csv",
        family_rows,
        [
            "family",
            "keeper",
            "n_members",
            "members",
            "mapx_keep",
            "mapx_archive",
            "member_detail",
        ],
    )

    source_rows = [
        {
            "name": r["name"],
            "layer_kind": r["layer_kind"],
            "tier": r["tier"],
            "mapx_action": r["mapx_action"],
            "source_status": r["source_status"],
            "source_note": r["source_note"],
            "postgres_table": r["postgres_table"],
            "store_type": r["store_type"],
        }
        for r in records
    ]
    write_csv(
        HERE / "source_availability.csv",
        source_rows,
        [
            "name",
            "layer_kind",
            "tier",
            "mapx_action",
            "source_status",
            "source_note",
            "postgres_table",
            "store_type",
        ],
    )

    def count(pred) -> int:
        return sum(1 for r in records if pred(r))

    p1 = [r for r in records if r["tier"] == "P1"]
    write_csv(
        HERE / "p1_publish_candidates.csv",
        [
            {
                "name": r["name"],
                "layer_kind": r["layer_kind"],
                "title": r["title"],
                "theme": r["theme"],
                "country_scope": r["country_scope"],
                "srs": r["srs"],
                "score_total": r["score_total"],
                "source_status": r["source_status"],
                "source_note": r["source_note"],
                "mapx_action": r["mapx_action"],
            }
            for r in p1
        ],
        [
            "name",
            "layer_kind",
            "title",
            "theme",
            "country_scope",
            "srs",
            "score_total",
            "source_status",
            "source_note",
            "mapx_action",
        ],
    )
    lines = []
    lines.append("Sustainable Caucasus GeoNode -> MapX characterization")
    lines.append(f"Layers scored: {len(records)}")
    lines.append(
        f"Vector: {count(lambda r: r['layer_kind']=='vector')} | "
        f"Raster: {count(lambda r: r['layer_kind']=='raster')}"
    )
    lines.append("")
    for tier in ("P1", "P2", "P3", "P4"):
        n = count(lambda r, t=tier: r["tier"] == t)
        nv = count(lambda r, t=tier: r["tier"] == t and r["layer_kind"] == "vector")
        nr = count(lambda r, t=tier: r["tier"] == t and r["layer_kind"] == "raster")
        lines.append(f"{tier}: {n}  (vector {nv}, raster {nr})")
    lines.append("")
    lines.append("MapX actions:")
    for action in ("publish", "review", "archive", "drop_demo"):
        lines.append(f"  {action}: {count(lambda r, a=action: r['mapx_action']==a)}")
    lines.append("")
    lines.append("Source files in local archive:")
    for status in sorted({r["source_status"] for r in records}):
        lines.append(f"  {status}: {count(lambda r, s=status: r['source_status']==s)}")
    lines.append("")
    missing = [r for r in records if r["source_status"].startswith("missing")]
    lines.append("")
    lines.append(f"Missing source files: {len(missing)}")
    for rec in missing:
        lines.append(
            f"  [{rec['tier']}] {rec['layer_kind']} {rec['name']}  |  {rec['source_status']}"
        )
    lines.append("")
    lines.append(f"P1 publish list ({len(p1)} layers) - validate before MapX ingest:")
    for rec in p1:
        src = "OK" if rec["source_status"] == "found" else rec["source_status"]
        lines.append(
            f"  [{rec['layer_kind'][:1].upper()}] {rec['name']}  |  "
            f"{rec['title'][:70]}  |  score {rec['score_total']}  |  {rec['theme']}  |  {src}"
        )
    summary = "\n".join(lines) + "\n"
    (HERE / "characterization_summary.txt").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
