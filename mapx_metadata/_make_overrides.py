#!/usr/bin/env python3
"""Generate curated MapX text overrides from GeoNode abstracts (one entry per layer)."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CATALOG = HERE / "triage" / "publication_catalog.csv"
CHAR = HERE / "triage" / "layer_characterization.csv"
OUT = HERE / "mapx_metadata" / "_text_overrides.json"

URL_RE = re.compile(r"https?://[^\s\)\]>,\"']+", re.I)


def polish(raw: str) -> str:
    if not raw:
        return ""
    text = raw.strip()
    reps = [
        ("This layers shows", "Dataset showing"),
        ("This layers ", "Dataset covering "),
        ("This layer shows", "Dataset showing"),
        ("This layer has been downloaded from", "Dataset obtained from"),
        ("This layer represents", "Dataset representing"),
        ("This layer has been created by", "Derived by"),
        ("This raster shows", "Raster dataset showing"),
        ("Here is the glacier outlines from", "Glacier outlines from"),
        ("Here is the", "Dataset from"),
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
        ("containes", "contains"),
        ("Responcse", "Response"),
        ("moutain", "mountain"),
        ("It is topologically", "Topologically"),
        ("It is fully connected", "Fully connected"),
        ("GIS data shows", "Spatial dataset showing"),
        ("GIS layer provides", "Spatial dataset providing"),
        ("This is a map of", "Map of"),
        ("This is a map shows", "Map showing"),
        ("This map shows", "Map showing"),
        ("This map represents", "Map representing"),
        ("This map was prepared", "Prepared"),
        ("Map shows", "Map showing"),
        ("Digital map shows", "Digital map showing"),
        ("  ", " "),
    ]
    for a, b in reps:
        text = text.replace(a, b)
    text = re.sub(r"\s+", " ", text).strip()
    if text and not text.endswith("."):
        text += "."
    return text


def notes_html(bullets: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>"


def urls_from(text: str) -> list[dict]:
    out, seen = [], set()
    for u in URL_RE.findall(text or ""):
        u = u.rstrip(").,;")
        if u in seen:
            continue
        seen.add(u)
        host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", u).split("/")[0])
        out.append(
            {
                "is_download_link": u.lower().endswith((".zip", ".tif", ".gpkg", ".shp", ".gz", ".pdf")),
                "url": u,
                "label": host or u,
            }
        )
    return out


# High-quality hand polish for flagship layers (match user IFL example quality)
HAND = {
    "IFL_2013_Caucasus": {
        "title": "Caucasus Intact Forests 2013",
        "abstract": (
            "Extent of Intact Forest Landscapes (IFLs) in the Caucasus region in 2013. "
            "Intact Forest Landscapes are large, continuous areas of natural ecosystems that show no significant "
            "signs of human activity or habitat fragmentation. The dataset provides an updated assessment of forest "
            "integrity across the Caucasus and serves as a reference for evaluating changes in forest condition, "
            "biodiversity conservation, and ecosystem connectivity over time."
        ),
        "notes": notes_html(
            [
                "Intact Forest Landscapes (IFLs) are unfragmented natural ecosystems large enough to maintain native biodiversity and ecological processes.",
                "The layer represents forest conditions in 2013.",
                "IFL boundaries were derived from satellite imagery and ancillary environmental datasets.",
                "The dataset supports assessments of forest integrity, habitat connectivity, and conservation planning.",
                "This layer can be compared with the 2000 IFL dataset to identify areas of forest loss, fragmentation, or persistence.",
            ]
        ),
        "data_attribution": "Intact Forest Landscapes Project, Transparent World, and Global Forest Watch.",
        "citation": (
            "Potapov, P., Yaroshenko, A., Turubanova, S., Hansen, M.C., et al. Intact Forest Landscapes of the World "
            "(2013 baseline). Intact Forest Landscapes Project. Available through https://www.intactforests.org."
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://www.intactforests.org",
                "label": "Intact Forest Landscapes Project",
            },
            {
                "is_download_link": True,
                "url": "https://storage.googleapis.com/ifl-files/IFL_2013.zip",
                "label": "Global Intact Forest Landscapes 2013 Dataset",
            },
        ],
        "license_text": (
            "Please refer to the original data provider's terms of use and licensing conditions available at "
            "https://www.intactforests.org."
        ),
    },
    "IFL_2000_Caucasus": {
        "title": "Caucasus Intact Forests 2000",
        "abstract": (
            "Extent of Intact Forest Landscapes (IFLs) in the Caucasus region in 2000. "
            "IFLs are large, continuous areas of natural ecosystems without significant human disturbance or "
            "fragmentation. The 2000 baseline supports comparison with later IFL assessments to track forest "
            "integrity, habitat connectivity, and conservation status across the Caucasus ecoregion."
        ),
        "notes": notes_html(
            [
                "Baseline Intact Forest Landscapes for year 2000.",
                "Clipped to the Caucasus ecoregion extent from the global IFL product.",
                "Compare with the 2013 IFL layer and the 2000–2013 difference layer.",
            ]
        ),
        "data_attribution": "Intact Forest Landscapes Project, Transparent World, and Global Forest Watch.",
        "citation": (
            "Potapov, P. et al. Intact Forest Landscapes of the World (2000 baseline). "
            "Intact Forest Landscapes Project. https://www.intactforests.org."
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://www.intactforests.org",
                "label": "Intact Forest Landscapes Project",
            }
        ],
        "license_text": (
            "Please refer to the original data provider's terms of use and licensing conditions available at "
            "https://www.intactforests.org."
        ),
    },
    "IFL_difference_2000_2013_Caucasus": {
        "title": "Caucasus Intact Forests Difference 2000–2013",
        "abstract": (
            "Symmetrical difference between Intact Forest Landscapes in the Caucasus for 2000 and 2013. "
            "Highlights areas of IFL loss, gain, or change between the two baselines and supports analysis of "
            "forest fragmentation and integrity trends in the ecoregion."
        ),
        "notes": notes_html(
            [
                "Derived by geoprocessing a symmetrical difference between IFL 2000 and IFL 2013.",
                "Use together with the 2000 and 2013 IFL layers for change assessment.",
            ]
        ),
        "data_attribution": "Intact Forest Landscapes Project; difference computed in the Sustainable Caucasus archive.",
        "citation": (
            "Derived from Intact Forest Landscapes 2000 and 2013 baselines (https://www.intactforests.org) "
            "via symmetrical difference for the Caucasus ecoregion."
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://www.intactforests.org",
                "label": "Intact Forest Landscapes Project",
            }
        ],
    },
    "caucasus_glaciers": {
        "title": "Caucasus Glaciers (RGI 6.0)",
        "abstract": (
            "Glacier outlines for the Caucasus region from the Randolph Glacier Inventory (RGI) version 6.0. "
            "Outlines were produced by digitising ASTER imagery and provide a regional inventory of glacier "
            "extent for cryosphere monitoring, hydrological assessment, climate-impact studies, and conservation planning."
        ),
        "notes": notes_html(
            [
                "Source product: Randolph Glacier Inventory (RGI) 6.0; outlines digitised from ASTER imagery.",
                "Attribute schema follows RGI conventions (RGIId, GLIMSId, Area in km², elevation statistics, etc.).",
                "Survey dates (BgnDate–EndDate) can vary by glacier; interpret temporal coverage carefully.",
                "Caucasus subset compiled in the Sustainable Caucasus archive; not a substitute for the latest national glacier inventories.",
                "Compare with GLIMS glacier polygons where multi-source validation is required.",
            ]
        ),
        "data_attribution": (
            "RGI Consortium (2017). Randolph Glacier Inventory — A Dataset of Global Glacier Outlines, Version 6. "
            "NSIDC / GLIMS."
        ),
        "citation": (
            "RGI Consortium (2017). Randolph Glacier Inventory 6.0. "
            "https://www.glims.org/RGI/. Caucasus subset, Sustainable Caucasus GeoNode archive."
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://www.glims.org/RGI/",
                "label": "Randolph Glacier Inventory (GLIMS/RGI)",
            },
            {
                "is_download_link": False,
                "url": "https://nsidc.org/data/nsidc-0770",
                "label": "NSIDC RGI documentation",
            },
        ],
        "license_text": (
            "Use and citation of RGI data should follow GLIMS/RGI guidance at https://www.glims.org/RGI/ "
            "and the associated NSIDC dataset documentation."
        ),
        "years": ["2017"],
        "temporal": {
            "issuance": {
                "periodicity": "notPlanned",
                "released_at": "2017-01-01",
                "modified_at": "2017-01-01",
            },
            "range": {
                "is_timeless": False,
                "start_at": "2000-01-01",
                "end_at": "2017-12-31",
            },
        },
    },
    "ESA2000_Cauc": {
        "title": "Caucasus Land Cover 2000",
        "abstract": (
            "Land-cover classification for the Caucasus ecoregion for year 2000, derived from the ESA Climate "
            "Change Initiative Land Cover product and cropped to the Caucasus ecoregion boundary. Supports "
            "land-system change analysis, habitat assessment, and environmental reporting."
        ),
        "notes": notes_html(
            [
                "Source: ESA CCI Land Cover; cropped to the Caucasus ecoregion.",
                "Raster classes follow the ESA CCI land-cover legend; consult the Product User Guide for class definitions.",
                "Compare carefully with ESA2005/ESA2010 products when analysing change.",
            ]
        ),
        "data_attribution": "European Space Agency (ESA) Climate Change Initiative — Land Cover.",
        "citation": (
            "ESA CCI Land Cover (2000). Cropped to the Caucasus ecoregion. "
            "https://www.esa-landcover-cci.org"
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://www.esa-landcover-cci.org",
                "label": "ESA CCI Land Cover",
            }
        ],
        "license_text": "Refer to ESA CCI Land Cover terms of use at https://www.esa-landcover-cci.org.",
    },
    "ESA2005_Cauc": {
        "title": "Caucasus Land Cover 2005",
        "abstract": (
            "Land-cover classification for the Caucasus ecoregion for year 2005, derived from the ESA Climate "
            "Change Initiative Land Cover product and cropped to the Caucasus ecoregion boundary. Supports "
            "land-system change analysis, habitat assessment, and environmental reporting."
        ),
        "notes": notes_html(
            [
                "Source: ESA CCI Land Cover; cropped to the Caucasus ecoregion.",
                "MapX view ID in the catalog may be flagged wrong_layer — confirm the published WMS layer before pasting metadata.",
            ]
        ),
        "data_attribution": "European Space Agency (ESA) Climate Change Initiative — Land Cover.",
        "citation": (
            "ESA CCI Land Cover (2005). Cropped to the Caucasus ecoregion. "
            "https://www.esa-landcover-cci.org"
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://www.esa-landcover-cci.org",
                "label": "ESA CCI Land Cover",
            }
        ],
        "license_text": "Refer to ESA CCI Land Cover terms of use at https://www.esa-landcover-cci.org.",
    },
    "ESA2010_Cauc": {
        "title": "Caucasus Land Cover 2010",
        "abstract": (
            "Land-cover classification for the Caucasus ecoregion for year 2010, derived from the ESA Climate "
            "Change Initiative Land Cover product and cropped to the Caucasus ecoregion boundary. Supports "
            "land-system change analysis, habitat assessment, and environmental reporting."
        ),
        "notes": notes_html(
            [
                "Source: ESA CCI Land Cover; cropped to the Caucasus ecoregion.",
                "MapX view ID in the catalog may be flagged wrong_layer — confirm the published WMS layer before pasting metadata.",
            ]
        ),
        "data_attribution": "European Space Agency (ESA) Climate Change Initiative — Land Cover.",
        "citation": (
            "ESA CCI Land Cover (2010). Cropped to the Caucasus ecoregion. "
            "https://www.esa-landcover-cci.org"
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://www.esa-landcover-cci.org",
                "label": "ESA CCI Land Cover",
            }
        ],
        "license_text": "Refer to ESA CCI Land Cover terms of use at https://www.esa-landcover-cci.org.",
    },
    "GHS_2015": {
        "title": "Caucasus Population Density (2015)",
        "abstract": (
            "Population density for the Caucasus ecoregion in 2015 from the Global Human Settlement Layer (GHSL) "
            "population grid. Pixel values represent the number of people per 250 m cell. Supports demographic "
            "analysis, exposure assessment, and urban–rural planning at regional scale."
        ),
        "notes": notes_html(
            [
                "Unit: people per 250 m grid cell.",
                "Source: JRC GHSL population grid; cropped to the Caucasus ecoregion.",
                "Do not interpret as cadastral population counts; values are modelled grid estimates.",
            ]
        ),
        "data_attribution": "European Commission, Joint Research Centre — Global Human Settlement Layer (GHSL).",
        "citation": (
            "European Commission, JRC. GHSL population grid (2015). "
            "http://ghsl.jrc.ec.europa.eu/ghs_pop.php. Cropped to the Caucasus ecoregion."
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "http://ghsl.jrc.ec.europa.eu/ghs_pop.php",
                "label": "GHSL population grid",
            }
        ],
        "license_text": "Refer to JRC GHSL licensing and citation guidance for the population grid product.",
    },
    "protect_areas": {
        "title": "Caucasus Protected Areas 2021",
        "abstract": (
            "Protected areas in the Caucasus based on October 2021 Protected Planet / WDPA data. Features are "
            "classified by IUCN management categories and support biodiversity conservation planning, gap analysis, "
            "and environmental reporting across the ecoregion."
        ),
        "notes": notes_html(
            [
                "Source: Protected Planet / WDPA (October 2021).",
                "Style classification attribute in MapX: IUCN_CAT.",
                "Boundaries and statuses can change; verify against Protected Planet for formal reporting.",
            ]
        ),
        "data_attribution": "UNEP-WCMC and IUCN — World Database on Protected Areas / Protected Planet.",
        "citation": (
            "UNEP-WCMC and IUCN (2021). Protected Planet / WDPA. "
            "https://www.protectedplanet.net/en. Caucasus subset, October 2021."
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://www.protectedplanet.net/en",
                "label": "Protected Planet",
            }
        ],
        "license_text": "Refer to Protected Planet / WDPA terms of use at https://www.protectedplanet.net/en.",
    },
    "WDPA_Caucasus": {
        "title": "Caucasus Protected Areas (IUCN classification)",
        "abstract": (
            "Caucasus subset of the World Database on Protected Areas (WDPA, June 2017 version), cropped to the "
            "Caucasus ecoregion extent. Features include IUCN protected-area classifications for regional conservation analysis."
        ),
        "data_attribution": "UNEP-WCMC and IUCN — World Database on Protected Areas / Protected Planet.",
        "citation": (
            "UNEP-WCMC and IUCN (June 2017). World Database on Protected Areas. "
            "https://www.protectedplanet.net/c/world-database-on-protected-areas. Cropped to the Caucasus ecoregion."
        ),
    },
    "emerald_2020_epsg4326_caucasus": {
        "title": "Caucasus Emerald Network Sites 2020",
        "abstract": (
            "Emerald Network sites in the Caucasus region (EPSG:4326), compiled for the Sustainable Caucasus "
            "archive. The Emerald Network is an ecological network of Areas of Special Conservation Interest "
            "under the Bern Convention."
        ),
        "notes": notes_html(
            [
                "No GeoNode abstract was available; description inferred from layer name and theme.",
                "Coordinate reference system: EPSG:4326.",
                "Verify site status and boundaries against the official Emerald Network / Bern Convention sources before formal reporting.",
            ]
        ),
        "data_attribution": "Emerald Network / Bern Convention data as compiled in the Sustainable Caucasus GeoNode archive.",
        "citation": "Emerald Network sites for the Caucasus (2020), Sustainable Caucasus GeoNode archive (EPSG:4326).",
    },
    "sum_of_average_daily_air_temperatures_above__10c": {
        "title": "Armenia Sum of Average Daily Air Temperatures Above 10°C",
        "abstract": (
            "Cumulative sum of average daily air temperatures above 10°C for Armenia. Supports agro-climatic "
            "zoning, growing-season analysis, and renewable-energy related assessments within the Sustainable "
            "Caucasus climate GIS collection."
        ),
        "notes": notes_html(
            [
                "No GeoNode abstract was available; description inferred from the layer title.",
                "National coverage: Armenia.",
                "Values classify cumulative temperature sums relevant to growing-season analysis.",
            ]
        ),
        "data_attribution": "Sustainable Caucasus / Armenian climate GIS products.",
        "citation": (
            "Sum of average daily air temperatures above 10°C — Armenia. "
            "Sustainable Caucasus GeoNode archive."
        ),
    },
    "hydroshed_main_rivers_Caucasus": {
        "title": "Caucasus Main Rivers (HydroSHEDS)",
        "abstract": (
            "Main river network of the Caucasus ecoregion derived from the HydroSHEDS global hydrographic "
            "database. Source river lines were cropped to the Caucasus ecoregion boundary and filtered to "
            "retain principal channels. Supports hydrological mapping, basin analysis, freshwater connectivity "
            "assessment, and regional environmental planning."
        ),
        "notes": notes_html(
            [
                "Source: HydroSHEDS river network; Caucasus ecoregion subset with main rivers filtered.",
                "UP_CELLS indicates upstream contributing cells (flow accumulation proxy).",
                "HydroSHEDS is derived primarily from SRTM elevation; local channel position may differ from surveyed hydrography.",
                "Bounding box is approximate Caucasus extent; use MapX Update values from source for precision.",
                "Homepage: https://www.hydrosheds.org/",
            ]
        ),
        "data_attribution": "HydroSHEDS (WWF / USGS and partners).",
        "citation": (
            "Lehner, B., Verdin, K., Jarvis, A. (2008). HydroSHEDS. World Wildlife Fund US / USGS. "
            "https://www.hydrosheds.org/. Caucasus main-rivers subset, Sustainable Caucasus archive."
        ),
        "years": ["2008"],
        "temporal": {
            "issuance": {
                "periodicity": "notPlanned",
                "released_at": "2008-01-01",
                "modified_at": "2008-01-01",
            },
            "range": {
                "is_timeless": True,
                "start_at": "0001-01-01",
                "end_at": "0001-01-01",
            },
        },
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://www.hydrosheds.org/",
                "label": "HydroSHEDS",
            }
        ],
        "license_name": "HydroSHEDS terms",
        "license_text": (
            "HydroSHEDS data use is subject to the HydroSHEDS licence and citation requirements. "
            "See https://www.hydrosheds.org/page/license."
        ),
        "keywords": {
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
            "keys_m49": ["ARM", "AZE", "IRN", "TUR", "RUS", "GEO"],
            "keys_gemet": ["2924", "4612"],
            "keys_topic": ["inlandWaters"],
        },
    },
    "caucasus_population_density_2020": {
        "title": "Caucasus Population Density 2020",
        "abstract": (
            "Population density of the Caucasus for 2020 by NUTS3 units, expressed as people per km2. "
            "Values are compiled from national statistical offices of Armenia, Azerbaijan, Georgia, Iran, "
            "Russia and Turkey. Supports demographic analysis, exposure assessment and regional planning."
        ),
        "notes": notes_html(
            [
                "Unit: people per km2 at NUTS3 level.",
                "Source offices: Armstat, Stat.gov.az, GeoStat, Amar, Rosstat, TurkStat.",
                "Style classification in MapX uses numeric field pop_densit (range classes); see style paste guide.",
                "Bounding box is approximate Caucasus extent; use MapX Update values from source for precision.",
            ]
        ),
        "data_attribution": (
            "National statistical offices of Armenia, Azerbaijan, Georgia, Iran, Russia and Turkey; "
            "Sustainable Caucasus compilation."
        ),
        "citation": (
            "Caucasus population density 2020 (NUTS3). Sustainable Caucasus GeoNode archive. "
            "Compiled from national statistical offices (Armstat, Stat.az, GeoStat, Amar, Rosstat, TurkStat)."
        ),
        "license_name": "Provider terms",
        "license_text": (
            "Refer to each national statistical office terms of use. Links listed under origin sources."
        ),
        "years": ["2020"],
    },
    "Forest_height_2019_NAFR_Caucasus_Ecoregion": {
        "title": "Caucasus Ecoregion Forest Canopy Height 2019",
        "abstract": (
            "Global 30 m forest canopy height for 2019, subsampled to the Caucasus ecoregion. The product integrates "
            "GEDI lidar forest-structure measurements with Landsat analysis-ready time series. Pixel values 0–60 "
            "represent canopy height in metres; 101 = water; 102 = snow/ice; 103 = no data."
        ),
        "notes": notes_html(
            [
                "Pixel coding: 0–60 m canopy height; 101 water; 102 snow/ice; 103 no data.",
                "Source: GLAD/UMD GEDI–Landsat canopy height product.",
                "Use for forest structure, biomass proxies, and habitat connectivity studies.",
            ]
        ),
        "data_attribution": "GLAD / University of Maryland — GEDI–Landsat forest canopy height.",
        "citation": (
            "Potapov et al. Global forest canopy height 2019 (GEDI–Landsat). "
            "https://glad.umd.edu/dataset/gedi. Caucasus ecoregion subset."
        ),
        "source_urls": [
            {
                "is_download_link": False,
                "url": "https://glad.umd.edu/dataset/gedi",
                "label": "GLAD GEDI forest height",
            }
        ],
    },
}


def main() -> None:
    pub = [
        r
        for r in csv.DictReader(CATALOG.open(encoding="utf-8-sig"))
        if r.get("publish") == "yes"
    ]
    char = {r["name"]: r for r in csv.DictReader(CHAR.open(encoding="utf-8-sig"))}
    overrides: dict = {}

    for r in pub:
        name = r["geonode_name"]
        title = (r.get("title") or r.get("geonode_title") or name).strip()
        raw = (char.get(name, {}).get("abstract") or "").strip()
        if raw.lower() == "no abstract provided":
            raw = ""

        if name in HAND:
            overrides[name] = HAND[name]
            continue

        entry: dict = {"title": title}
        polished = polish(raw)
        if polished:
            # Expand very short abstracts slightly without inventing unsupported facts
            if len(polished) < 120:
                polished = (
                    f"{polished} The dataset is published in the Sustainable Caucasus "
                    f"GeoNode archive for regional mapping and decision support."
                )
            entry["abstract"] = polished

        bullets = [
            f"Theme/title: {title}.",
            "Compiled for the Sustainable Caucasus GeoNode → MapX publication workflow.",
        ]
        blob = (raw + " " + polished).lower()
        if "crop" in blob or "clip" in blob or "extent" in blob:
            bullets.append(
                "Spatial coverage limited to the Caucasus ecoregion / study area where noted in source metadata."
            )
        if r["layer_kind"] == "raster":
            bullets.append(
                "Raster values encode the thematic variable described in the abstract; check units before analysis."
            )
        else:
            bullets.append(
                "Vector attribute names follow the source GeoPackage schema; aliases are human-readable labels for MapX."
            )
        if "openstreetmap" in blob or "geofabrik" in blob:
            bullets.append("OpenStreetMap completeness varies by region and date of extract.")
        bullets.append(
            "Verify licensing, citation, and fitness-for-purpose with the original data provider before redistribution."
        )
        entry["notes"] = notes_html(bullets)
        years = re.findall(r"\b((?:19|20)\d{2})\b", f"{name} {title} {raw}")
        if years:
            entry["citation"] = (
                f"{title} ({years[0]}). Sustainable Caucasus GeoNode archive. "
                + (f"Source: {urls_from(raw)[0]['url']}." if urls_from(raw) else "")
            ).strip()
        else:
            entry["citation"] = (
                f"{title}. Sustainable Caucasus GeoNode / MapX publication archive."
            )

        src = urls_from(raw)
        if src:
            entry["source_urls"] = src

        # Family-specific attribution hints
        low = f"{name} {raw} {title}".lower()
        if "openstreetmap" in low or "geofabrik" in low or name.endswith("_roads") or name in {
            "roads_caucasus_select",
            "railroads",
            "caucasus_pois_clip_culture",
        }:
            entry["data_attribution"] = "© OpenStreetMap contributors."
            entry["license_text"] = (
                "OpenStreetMap data are available under the Open Database License (ODbL). "
                "https://www.openstreetmap.org/copyright"
            )
        elif "wwf" in low:
            entry["data_attribution"] = "Data provided by WWF (non-commercial use; credit required)."
        elif "firms" in low or name == "fires_2020":
            entry["data_attribution"] = "NASA FIRMS."
        elif "hydroshed" in low:
            entry["data_attribution"] = "HydroSHEDS."
        elif "glims" in low:
            entry["data_attribution"] = "GLIMS glacier database."
        elif "randolph" in low or name == "caucasus_glaciers":
            entry["data_attribution"] = "Randolph Glacier Inventory (RGI)."
        elif "gedi" in low or "glad.umd" in low:
            entry["data_attribution"] = "GLAD / UMD forest canopy height (GEDI–Landsat integration)."
        elif "preview" in low:
            entry["data_attribution"] = "UNEP/GRID-Geneva PREVIEW."
        elif "worldclim" in low:
            entry["data_attribution"] = "WorldClim."
        elif "unesco" in low or "whc.unesco" in low:
            entry["data_attribution"] = "UNESCO World Heritage Centre."
        elif "protectedplanet" in low or "wdpa" in low:
            entry["data_attribution"] = "UNEP-WCMC and IUCN — Protected Planet / WDPA."
        elif name.startswith("pop_") and ("georgia" in low or "geostat" in low):
            entry["data_attribution"] = "GeoStat (Georgia); GIS: GeoGraphic."
        elif any(
            x in name
            for x in (
                "caucasus_population",
                "caucasus_annual_growth",
                "caucasus_urbanization",
                "total_population",
            )
        ):
            entry["data_attribution"] = (
                "National statistical offices of Armenia, Azerbaijan, Georgia, Iran, "
                "Russia and Turkey; Sustainable Caucasus compilation."
            )
        elif "world bank" in low or "georisk" in low or "seismic" in low:
            entry["data_attribution"] = (
                "AIR Worldwide, GEM Foundation, and GEORISK (World Bank PSHA project for Armenia), where applicable."
            )

        overrides[name] = entry

    OUT.write_text(json.dumps(overrides, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(overrides)} overrides -> {OUT}")
    missing = [r["geonode_name"] for r in pub if r["geonode_name"] not in overrides]
    print("missing", missing)


if __name__ == "__main__":
    main()
