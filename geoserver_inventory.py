#!/usr/bin/env python3

import base64
import csv
import getpass
import json
import os
import re
import sys

from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen


OUTPUT = "/tmp/geoserver_layers_all_workspaces.csv"

BASE_URL = (
    os.environ.get("GEOSERVER_LOCATION")
    or "http://localhost:8080/geoserver"
).rstrip("/")

USER = (
    os.environ.get("GEOSERVER_ADMIN_USER")
    or "admin"
)

PASSWORD = os.environ.get("GEOSERVER_ADMIN_PASSWORD")

if not PASSWORD:
    PASSWORD = getpass.getpass("GeoServer admin password: ")

DATA_DIR = os.environ.get("GEOSERVER_DATA_DIR", "")


AUTH = base64.b64encode(
    f"{USER}:{PASSWORD}".encode("utf-8")
).decode("ascii")


# ------------------------------------------------------------
# Generic helpers
# ------------------------------------------------------------

def normalize_url(url):
    """
    GeoServer REST responses may contain externally-advertised URLs.
    Force REST requests back through BASE_URL.
    """
    if not url:
        return ""

    if url.startswith("http://") or url.startswith("https://"):
        marker = "/rest/"
        pos = url.find(marker)

        if pos >= 0:
            return BASE_URL + url[pos:]

        return url

    if url.startswith("/"):
        return BASE_URL + url

    return BASE_URL + "/" + url


def get_json(url):
    url = normalize_url(url)

    req = Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Basic {AUTH}",
        },
    )

    with urlopen(req) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def as_list(value):
    if value is None or value == "":
        return []

    if isinstance(value, list):
        return value

    return [value]


def text_or_json(value):
    """
    Keep simple values readable while serializing nested structures
    into compact one-line JSON suitable for CSV.
    """
    if value is None:
        return ""

    if isinstance(value, str):
        return value.replace("\r", " ").replace("\n", " ")

    if isinstance(value, (int, float, bool)):
        return str(value)

    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def flatten_strings(value):
    result = []

    if value is None:
        return result

    if isinstance(value, str):
        result.append(value)

    elif isinstance(value, list):
        for item in value:
            result.extend(flatten_strings(item))

    elif isinstance(value, dict):

        if "$" in value:
            result.extend(flatten_strings(value["$"]))

        elif "string" in value:
            result.extend(flatten_strings(value["string"]))

        else:
            for v in value.values():
                result.extend(flatten_strings(v))

    return result


def get_root(doc, *names):
    for name in names:
        if name in doc and isinstance(doc[name], dict):
            return name, doc[name]

    return "", {}


# ------------------------------------------------------------
# Store helpers
# ------------------------------------------------------------

def connection_parameters(store):
    """
    Convert GeoServer connectionParameters into a dictionary.

    Passwords are intentionally not returned later in the CSV.
    """
    result = {}

    cp = store.get("connectionParameters") or {}
    entries = cp.get("entry") or []

    for entry in as_list(entries):

        if not isinstance(entry, dict):
            continue

        key = (
            entry.get("@key")
            or entry.get("key")
        )

        value = (
            entry.get("$")
            if "$" in entry
            else entry.get("value")
        )

        if key is not None and value is not None:
            result[str(key)] = str(value)

    return result


def resolve_file_path(value):
    """
    Convert GeoServer file URLs to filesystem paths.

    Examples:
      file:/data/foo.tif
      file:///data/foo.tif
      file:data/geonode/foo.tif
    """
    if not value:
        return ""

    if not value.startswith("file:"):
        return value

    remainder = value[5:]

    if remainder.startswith("//"):
        path = unquote(urlsplit(value).path)
        return os.path.normpath(path)

    if remainder.startswith("/"):
        return os.path.normpath(
            unquote(remainder)
        )

    relative = unquote(remainder)

    if DATA_DIR:
        return os.path.normpath(
            os.path.join(
                DATA_DIR,
                relative,
            )
        )

    return value


def resolve_exact_file(source_path, native_name):
    """
    Some shapefile datastores point at a directory rather than directly
    at the .shp file. If possible, resolve it to the actual shapefile.
    """
    if not source_path or not native_name:
        return source_path

    if os.path.isdir(source_path):

        candidate = os.path.join(
            source_path,
            native_name + ".shp",
        )

        if os.path.isfile(candidate):
            return candidate

    return source_path


# ------------------------------------------------------------
# Bounding boxes
# ------------------------------------------------------------

def bbox_values(bbox, prefix):
    bbox = bbox or {}

    return {
        f"{prefix}_minx": bbox.get("minx", ""),
        f"{prefix}_miny": bbox.get("miny", ""),
        f"{prefix}_maxx": bbox.get("maxx", ""),
        f"{prefix}_maxy": bbox.get("maxy", ""),
        f"{prefix}_crs": text_or_json(
            bbox.get("crs")
        ),
    }


# ------------------------------------------------------------
# Vector attributes / geometry
# ------------------------------------------------------------

def extract_attributes(resource):

    attributes = as_list(
        (resource.get("attributes") or {}).get("attribute")
    )

    reduced = []

    geometry_column = ""
    geometry_type = ""

    for attr in attributes:

        if not isinstance(attr, dict):
            continue

        name = attr.get("name", "")
        binding = attr.get("binding", "")

        reduced.append({
            "name": name,
            "binding": binding,
            "nillable": attr.get("nillable"),
            "minOccurs": attr.get("minOccurs"),
            "maxOccurs": attr.get("maxOccurs"),
        })

        binding_lower = str(binding).lower()

        if (
            not geometry_column
            and (
                "jts.geom." in binding_lower
                or binding_lower.endswith(".geometry")
            )
        ):
            geometry_column = name
            geometry_type = str(binding).rsplit(".", 1)[-1]

    return (
        geometry_column,
        geometry_type,
        json.dumps(
            reduced,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )


# ------------------------------------------------------------
# Styles
# ------------------------------------------------------------

def style_scope(style_href):

    if not style_href:
        return ""

    path = unquote(
        urlsplit(style_href).path
    )

    match = re.search(
        r"/rest/workspaces/([^/]+)/styles/",
        path,
    )

    if match:
        return match.group(1)

    return "global"


def get_alternate_styles(qualified_name):

    url = (
        f"{BASE_URL}/rest/layers/"
        f"{quote(qualified_name, safe=':')}"
        f"/styles.json"
    )

    try:
        doc = get_json(url)

    except HTTPError as e:
        if e.code == 404:
            return "", ""
        raise

    items = as_list(
        (doc.get("styles") or {}).get("style")
    )

    names = []
    hrefs = []

    for item in items:

        if isinstance(item, dict):

            name = item.get("name")
            href = item.get("href")

            if name:
                names.append(str(name))

            if href:
                hrefs.append(str(href))

        elif item:
            names.append(str(item))

    return (
        "; ".join(names),
        "; ".join(hrefs),
    )


# ------------------------------------------------------------
# Workspaces
# ------------------------------------------------------------

print(
    "Retrieving GeoServer workspaces...",
    file=sys.stderr,
)

try:
    workspace_doc = get_json(
        f"{BASE_URL}/rest/workspaces.json"
    )

except Exception as e:
    print(
        f"ERROR retrieving workspaces: {e}",
        file=sys.stderr,
    )
    sys.exit(1)


workspace_items = as_list(
    (workspace_doc.get("workspaces") or {}).get("workspace")
)

workspaces = []

for item in workspace_items:

    if isinstance(item, dict):
        name = item.get("name")
    else:
        name = str(item)

    if name:
        workspaces.append(name)


print(
    f"Found {len(workspaces)} workspace(s)",
    file=sys.stderr,
)


# ------------------------------------------------------------
# Process layers
# ------------------------------------------------------------

rows = []
errors = []


for workspace in sorted(
    workspaces,
    key=str.lower,
):

    print(
        f"\nWorkspace: {workspace}",
        file=sys.stderr,
    )

    layers_url = (
        f"{BASE_URL}/rest/workspaces/"
        f"{quote(workspace)}/layers.json"
    )

    try:
        layer_listing = get_json(layers_url)

    except HTTPError as e:

        if e.code == 404:
            print(
                "  No layers / endpoint returned 404",
                file=sys.stderr,
            )
            continue

        errors.append(
            (workspace, "", str(e))
        )
        continue

    except Exception as e:
        errors.append(
            (workspace, "", str(e))
        )
        continue


    layer_items = as_list(
        (layer_listing.get("layers") or {}).get("layer")
    )

    print(
        f"  Layers: {len(layer_items)}",
        file=sys.stderr,
    )


    for item in layer_items:

        if isinstance(item, dict):
            layer_name = item.get("name", "")
        else:
            layer_name = str(item)

        if not layer_name:
            continue


        # Workspace listings normally return an unqualified name.
        # Remove workspace prefix if it is present anyway.
        if layer_name.startswith(workspace + ":"):
            short_name = layer_name.split(":", 1)[1]
        else:
            short_name = layer_name

        qualified_name = (
            f"{workspace}:{short_name}"
        )


        print(
            f"    {qualified_name}",
            file=sys.stderr,
        )


        try:

            # ----------------------------------------------------
            # Published layer object
            # ----------------------------------------------------

            layer_doc = get_json(
                f"{BASE_URL}/rest/layers/"
                f"{quote(qualified_name, safe=':')}.json"
            )

            layer = layer_doc["layer"]

            default_style = (
                layer.get("defaultStyle")
                or {}
            )

            default_style_name = (
                default_style.get("name", "")
            )

            default_style_href = (
                default_style.get("href", "")
            )

            default_style_scope = style_scope(
                default_style_href
            )

            alternate_style_names, alternate_style_hrefs = (
                get_alternate_styles(
                    qualified_name
                )
            )


            # ----------------------------------------------------
            # Underlying resource
            # ----------------------------------------------------

            resource_ref = (
                layer.get("resource")
                or {}
            )

            resource_class = resource_ref.get(
                "@class",
                "",
            )

            resource_href = resource_ref.get(
                "href",
                "",
            )

            if not resource_href:
                raise RuntimeError(
                    "Layer has no resource href"
                )


            resource_doc = get_json(
                resource_href
            )

            resource_type, resource = get_root(
                resource_doc,
                "featureType",
                "coverage",
                "wmsLayer",
                "wmtsLayer",
            )

            if not resource:
                raise RuntimeError(
                    "Unknown GeoServer resource type: "
                    + ", ".join(resource_doc.keys())
                )


            if resource_type == "featureType":
                layer_kind = "vector"

            elif resource_type == "coverage":
                layer_kind = "raster"

            elif resource_type == "wmsLayer":
                layer_kind = "external_wms"

            elif resource_type == "wmtsLayer":
                layer_kind = "external_wmts"

            else:
                layer_kind = "other"


            native_name = resource.get(
                "nativeName",
                "",
            )

            title = resource.get(
                "title",
                "",
            )

            abstract = resource.get(
                "abstract",
                "",
            )

            description = resource.get(
                "description",
                "",
            )

            keywords = flatten_strings(
                resource.get("keywords")
            )

            # Remove duplicates while preserving order.
            keywords = list(
                dict.fromkeys(keywords)
            )

            keyword_string = "; ".join(
                keywords
            )


            # ----------------------------------------------------
            # CRS / bounding boxes
            # ----------------------------------------------------

            srs = resource.get("srs", "")

            native_crs = text_or_json(
                resource.get("nativeCRS")
            )

            projection_policy = resource.get(
                "projectionPolicy",
                "",
            )

            native_bbox = bbox_values(
                resource.get(
                    "nativeBoundingBox"
                ),
                "native_bbox",
            )

            latlon_bbox = bbox_values(
                resource.get(
                    "latLonBoundingBox"
                ),
                "latlon_bbox",
            )


            # ----------------------------------------------------
            # Vector schema
            # ----------------------------------------------------

            geometry_column = ""
            geometry_type = ""
            attributes_json = ""

            if resource_type == "featureType":

                (
                    geometry_column,
                    geometry_type,
                    attributes_json,
                ) = extract_attributes(
                    resource
                )


            # ----------------------------------------------------
            # Store
            # ----------------------------------------------------

            store_ref = (
                resource.get("store")
                or {}
            )

            store_href = store_ref.get(
                "href",
                "",
            )

            store_name = ""
            store_type = ""
            store_enabled = ""
            store_dbtype = ""

            store_host = ""
            store_port = ""
            store_database = ""
            store_schema = ""

            source_path = ""
            postgres_schema = ""
            postgres_table = ""
            data_source = ""
            external_service_url = ""

            if store_href:

                store_doc = get_json(
                    store_href
                )

                store_root_type, store = get_root(
                    store_doc,
                    "dataStore",
                    "coverageStore",
                    "wmsStore",
                    "wmtsStore",
                )

                store_name = store.get(
                    "name",
                    "",
                )

                store_type = store.get(
                    "type",
                    "",
                )

                store_enabled = store.get(
                    "enabled",
                    "",
                )

                conn = connection_parameters(
                    store
                )

                store_dbtype = conn.get(
                    "dbtype",
                    "",
                )

                store_host = conn.get(
                    "host",
                    "",
                )

                store_port = conn.get(
                    "port",
                    "",
                )

                store_database = conn.get(
                    "database",
                    "",
                )

                store_schema = conn.get(
                    "schema",
                    "",
                )

                is_postgis = (
                    "postgis"
                    in str(store_type).lower()
                    or
                    "postgis"
                    in str(store_dbtype).lower()
                )


                if is_postgis:

                    postgres_schema = (
                        store_schema
                        or "public"
                    )

                    postgres_table = native_name

                    if postgres_table:
                        data_source = (
                            f"{postgres_schema}."
                            f"{postgres_table}"
                        )


                else:

                    raw_path = (
                        store.get("url")
                        or conn.get("url")
                        or ""
                    )

                    source_path = resolve_file_path(
                        raw_path
                    )

                    source_path = resolve_exact_file(
                        source_path,
                        native_name,
                    )

                    data_source = source_path


                # Cascaded WMS / WMTS source
                external_service_url = (
                    store.get("capabilitiesURL")
                    or store.get("url")
                    or ""
                )


            # ----------------------------------------------------
            # Raster / coverage-specific metadata
            # ----------------------------------------------------

            native_format = resource.get(
                "nativeFormat",
                "",
            )

            coverage_grid_json = text_or_json(
                resource.get("grid")
            )

            coverage_dimensions_json = text_or_json(
                resource.get("dimensions")
            )


            # ----------------------------------------------------
            # Miscellaneous metadata
            # ----------------------------------------------------

            metadata_links_json = text_or_json(
                resource.get("metadataLinks")
            )

            resource_metadata_json = text_or_json(
                resource.get("metadata")
            )

            layer_metadata_json = text_or_json(
                layer.get("metadata")
            )


            row = {
                "workspace": workspace,
                "name": short_name,
                "qualified_name": qualified_name,

                "layer_kind": layer_kind,

                "title": title,
                "abstract": abstract,
                "description": description,
                "keywords": keyword_string,

                "enabled": resource.get(
                    "enabled",
                    "",
                ),

                "advertised": resource.get(
                    "advertised",
                    "",
                ),

                "resource_type": resource_type,
                "resource_class": resource_class,
                "native_name": native_name,

                "srs": srs,
                "native_crs": native_crs,
                "projection_policy": projection_policy,

                "geometry_column": geometry_column,
                "geometry_type": geometry_type,
                "attributes_json": attributes_json,

                "default_style_name": default_style_name,
                "default_style_scope": default_style_scope,
                "default_style_href": default_style_href,

                "alternate_style_names": alternate_style_names,
                "alternate_style_hrefs": alternate_style_hrefs,

                "store_name": store_name,
                "store_type": store_type,
                "store_enabled": store_enabled,
                "store_dbtype": store_dbtype,

                # Useful connection metadata, but NO passwords.
                "store_host": store_host,
                "store_port": store_port,
                "store_database": store_database,
                "store_schema": store_schema,

                "data_source": data_source,
                "source_path": source_path,

                "postgres_schema": postgres_schema,
                "postgres_table": postgres_table,

                "native_format": native_format,
                "coverage_grid_json": coverage_grid_json,
                "coverage_dimensions_json": coverage_dimensions_json,

                "metadata_links_json": metadata_links_json,
                "resource_metadata_json": resource_metadata_json,
                "layer_metadata_json": layer_metadata_json,

                # Useful later if this layer is served by GeoServer WMS.
                "wms_layer_name": qualified_name,

                # Relevant for cascaded WMS / WMTS stores.
                "external_service_url": external_service_url,
            }

            row.update(native_bbox)
            row.update(latlon_bbox)

            rows.append(row)


        except Exception as e:

            errors.append(
                (
                    workspace,
                    short_name,
                    str(e),
                )
            )

            print(
                f"      WARNING: {e}",
                file=sys.stderr,
            )


# ------------------------------------------------------------
# CSV
# ------------------------------------------------------------

rows.sort(
    key=lambda x: (
        x["workspace"].lower(),
        x["name"].lower(),
    )
)


fields = [
    "workspace",
    "name",
    "qualified_name",

    "layer_kind",

    "title",
    "abstract",
    "description",
    "keywords",

    "enabled",
    "advertised",

    "resource_type",
    "resource_class",
    "native_name",

    "srs",
    "native_crs",
    "projection_policy",

    "native_bbox_minx",
    "native_bbox_miny",
    "native_bbox_maxx",
    "native_bbox_maxy",
    "native_bbox_crs",

    "latlon_bbox_minx",
    "latlon_bbox_miny",
    "latlon_bbox_maxx",
    "latlon_bbox_maxy",
    "latlon_bbox_crs",

    "geometry_column",
    "geometry_type",
    "attributes_json",

    "default_style_name",
    "default_style_scope",
    "default_style_href",

    "alternate_style_names",
    "alternate_style_hrefs",

    "store_name",
    "store_type",
    "store_enabled",
    "store_dbtype",

    "store_host",
    "store_port",
    "store_database",
    "store_schema",

    "data_source",
    "source_path",

    "postgres_schema",
    "postgres_table",

    "native_format",
    "coverage_grid_json",
    "coverage_dimensions_json",

    "metadata_links_json",
    "resource_metadata_json",
    "layer_metadata_json",

    "wms_layer_name",
    "external_service_url",
]


with open(
    OUTPUT,
    "w",
    newline="",
    encoding="utf-8",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields,
    )

    writer.writeheader()
    writer.writerows(rows)


print()
print(f"CSV written to : {OUTPUT}")
print(f"Workspaces     : {len(workspaces)}")
print(f"Layers exported: {len(rows)}")
print(f"Errors         : {len(errors)}")


if errors:

    print()
    print("Errors:")

    for workspace, layer, error in errors:

        if layer:
            print(
                f"  {workspace}:{layer}: {error}"
            )
        else:
            print(
                f"  {workspace}: {error}"
            )
