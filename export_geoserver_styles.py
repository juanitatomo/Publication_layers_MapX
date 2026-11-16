#!/usr/bin/env python3

import base64
import csv
import getpass
import json
import os
import re
import shutil
import sys

from collections import defaultdict
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen


# ============================================================
# Configuration
# ============================================================

INPUT_CSV = "/tmp/geoserver_layers_all_workspaces.csv"

EXPORT_DIR = "/tmp/geoserver_export"

STYLES_DIR = os.path.join(
    EXPORT_DIR,
    "styles",
)

METADATA_DIR = os.path.join(
    EXPORT_DIR,
    "style_metadata",
)

MANIFEST = os.path.join(
    EXPORT_DIR,
    "style_manifest.csv",
)


# ============================================================
# GeoServer connection
# ============================================================

BASE_URL = (
    os.environ.get("GEOSERVER_LOCATION")
    or "http://localhost:8080/geoserver"
).rstrip("/")

USER = (
    os.environ.get("GEOSERVER_ADMIN_USER")
    or "admin"
)

PASSWORD = os.environ.get(
    "GEOSERVER_ADMIN_PASSWORD"
)

if not PASSWORD:
    PASSWORD = getpass.getpass(
        "GeoServer admin password: "
    )


AUTH = base64.b64encode(
    f"{USER}:{PASSWORD}".encode("utf-8")
).decode("ascii")


# ============================================================
# Generic HTTP helpers
# ============================================================

def normalize_url(url):
    """
    GeoServer REST responses may contain the externally
    advertised URL.

    Force REST requests back through BASE_URL so that the
    script works correctly from inside the container.
    """

    if not url:
        return ""

    marker = "/rest/"
    pos = url.find(marker)

    if pos >= 0:
        return BASE_URL + url[pos:]

    if url.startswith("/"):
        return BASE_URL + url

    return url


def request_bytes(url, accept="*/*"):
    """
    Perform authenticated GET and return:

        body, content_type
    """

    url = normalize_url(url)

    req = Request(
        url,
        headers={
            "Authorization": f"Basic {AUTH}",
            "Accept": accept,
        },
    )

    with urlopen(req) as response:

        body = response.read()

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        return body, content_type


def get_json(url):

    body, _ = request_bytes(
        url,
        "application/json",
    )

    return json.loads(
        body.decode("utf-8")
    )


def as_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


# ============================================================
# Path / name helpers
# ============================================================

def safe_name(value):
    """
    Make a GeoServer object name safe for use as a local
    filename/directory name.
    """

    value = str(value)

    value = value.replace("/", "_")
    value = value.replace("\\", "_")
    value = value.replace("\x00", "_")

    return value


def strip_representation_extension(url):
    """
    Convert for example:

        .../styles/roads.json

    to:

        .../styles/roads
    """

    url = normalize_url(url)

    # Remove query string first.
    url = url.split("?", 1)[0]

    return re.sub(
        r"\.(json|xml|html)$",
        "",
        url,
        flags=re.IGNORECASE,
    )


def metadata_url(style_href):
    """
    Ensure style metadata is requested as JSON.
    """

    base = strip_representation_extension(
        style_href
    )

    return base + ".json"


def style_scope_from_href(style_href):
    """
    Return:

        global

    or the workspace name.
    """

    if not style_href:
        return ""

    path = unquote(
        urlsplit(
            normalize_url(style_href)
        ).path
    )

    match = re.search(
        r"/rest/workspaces/([^/]+)/styles/",
        path,
    )

    if match:
        return match.group(1)

    if "/rest/styles/" in path:
        return "global"

    return ""


def extension_from_filename(filename):

    if not filename:
        return ""

    basename = os.path.basename(filename)

    _, ext = os.path.splitext(basename)

    return ext.lower()


# ============================================================
# Style format helpers
# ============================================================

def native_mimetype(style_format, language_version):
    """
    Return the GeoServer media type used to retrieve the
    native style representation.
    """

    fmt = (
        style_format
        or ""
    ).strip().lower()

    version = (
        language_version
        or ""
    ).strip()


    if fmt in ("sld", "se"):

        # SLD / SE 1.1
        if version.startswith("1.1"):
            return "application/vnd.ogc.se+xml"

        # SLD 1.0
        return "application/vnd.ogc.sld+xml"


    if fmt in (
        "css",
        "geocss",
    ):
        return "application/vnd.geoserver.geocss+css"


    if fmt in (
        "ysld",
        "yaml",
    ):
        return "application/vnd.geoserver.ysld+yaml"


    if fmt in (
        "mbstyle",
        "mapbox",
    ):
        return "application/vnd.geoserver.mbstyle+json"


    return ""


def default_extension(style_format):

    fmt = (
        style_format
        or ""
    ).strip().lower()

    mapping = {
        "sld": ".sld",
        "se": ".sld",
        "css": ".css",
        "geocss": ".css",
        "ysld": ".yaml",
        "yaml": ".yaml",
        "mbstyle": ".json",
        "mapbox": ".json",
    }

    return mapping.get(
        fmt,
        ".style",
    )


def download_native_style(
    style_href,
    style_format,
    filename,
    language_version,
):
    """
    Download the native style body.

    First preference:
      request the style endpoint using the GeoServer native
      media type.

    Fallback:
      use the original filename extension.
    """

    base = strip_representation_extension(
        style_href
    )

    mime = native_mimetype(
        style_format,
        language_version,
    )

    first_error = None


    # --------------------------------------------------------
    # Preferred method: Accept native GeoServer style MIME
    # --------------------------------------------------------

    if mime:

        try:

            body, content_type = request_bytes(
                base,
                mime,
            )

            return (
                body,
                content_type,
                "native-mimetype",
            )

        except Exception as e:
            first_error = e


    # --------------------------------------------------------
    # Fallback: request by original extension
    # --------------------------------------------------------

    ext = extension_from_filename(
        filename
    )

    if not ext:
        ext = default_extension(
            style_format
        )

    try:

        body, content_type = request_bytes(
            base + ext,
            "*/*",
        )

        return (
            body,
            content_type,
            "filename-extension",
        )

    except Exception:

        if first_error:
            raise first_error

        raise


# ============================================================
# Read the layer inventory
# ============================================================

if not os.path.isfile(INPUT_CSV):

    print(
        f"ERROR: inventory CSV not found: {INPUT_CSV}",
        file=sys.stderr,
    )

    sys.exit(1)


os.makedirs(
    EXPORT_DIR,
    exist_ok=True,
)

os.makedirs(
    STYLES_DIR,
    exist_ok=True,
)

os.makedirs(
    METADATA_DIR,
    exist_ok=True,
)


# Keep the inventory alongside the style export.
inventory_copy = os.path.join(
    EXPORT_DIR,
    os.path.basename(INPUT_CSV),
)

shutil.copy2(
    INPUT_CSV,
    inventory_copy,
)


# ============================================================
# Build style -> layer usage map
# ============================================================

# Key:
#
#   (style_scope, style_name)
#
# Value:
#
#   {
#       "layers": set(),
#       "roles": set(),
#       "hrefs": set(),
#   }

usage = defaultdict(
    lambda: {
        "layers": set(),
        "roles": set(),
        "hrefs": set(),
    }
)


# Styles where scope could not be established.
unresolved_usage = []


with open(
    INPUT_CSV,
    newline="",
    encoding="utf-8",
) as f:

    reader = csv.DictReader(f)

    required = {
        "workspace",
        "name",
        "default_style_name",
        "default_style_href",
        "alternate_style_names",
        "alternate_style_hrefs",
    }

    missing = (
        required
        - set(reader.fieldnames or [])
    )

    if missing:

        print(
            "ERROR: inventory CSV is missing columns: "
            + ", ".join(sorted(missing)),
            file=sys.stderr,
        )

        sys.exit(1)


    for row in reader:

        workspace = (
            row.get("workspace")
            or ""
        ).strip()

        layer_name = (
            row.get("name")
            or ""
        ).strip()

        qualified_layer = (
            f"{workspace}:{layer_name}"
            if workspace
            else layer_name
        )


        # ----------------------------------------------------
        # Default style
        # ----------------------------------------------------

        style_name = (
            row.get("default_style_name")
            or ""
        ).strip()

        style_href = (
            row.get("default_style_href")
            or ""
        ).strip()

        style_scope = (
            row.get("default_style_scope")
            or ""
        ).strip()

        if not style_scope and style_href:
            style_scope = style_scope_from_href(
                style_href
            )


        if style_name:

            if style_scope:

                key = (
                    style_scope,
                    style_name,
                )

                usage[key]["layers"].add(
                    qualified_layer
                )

                usage[key]["roles"].add(
                    "default"
                )

                if style_href:
                    usage[key]["hrefs"].add(
                        style_href
                    )

            else:

                unresolved_usage.append({
                    "layer": qualified_layer,
                    "role": "default",
                    "name": style_name,
                    "href": style_href,
                })


        # ----------------------------------------------------
        # Alternate styles
        # ----------------------------------------------------

        alternate_names = [
            value.strip()
            for value in (
                row.get(
                    "alternate_style_names"
                )
                or ""
            ).split(";")
            if value.strip()
        ]

        alternate_hrefs = [
            value.strip()
            for value in (
                row.get(
                    "alternate_style_hrefs"
                )
                or ""
            ).split(";")
            if value.strip()
        ]


        if (
            alternate_names
            and
            len(alternate_names)
            != len(alternate_hrefs)
        ):

            print(
                "WARNING: alternate style names/hrefs "
                f"do not match for {qualified_layer}: "
                f"{len(alternate_names)} names, "
                f"{len(alternate_hrefs)} hrefs",
                file=sys.stderr,
            )


        for index, style_name in enumerate(
            alternate_names
        ):

            style_href = ""

            if index < len(alternate_hrefs):
                style_href = alternate_hrefs[index]

            style_scope = ""

            if style_href:
                style_scope = style_scope_from_href(
                    style_href
                )


            if style_scope:

                key = (
                    style_scope,
                    style_name,
                )

                usage[key]["layers"].add(
                    qualified_layer
                )

                usage[key]["roles"].add(
                    "alternate"
                )

                if style_href:
                    usage[key]["hrefs"].add(
                        style_href
                    )

            else:

                unresolved_usage.append({
                    "layer": qualified_layer,
                    "role": "alternate",
                    "name": style_name,
                    "href": style_href,
                })


# ============================================================
# Enumerate every GeoServer workspace
# ============================================================

print(
    "Retrieving GeoServer workspaces...",
    file=sys.stderr,
)

workspace_doc = get_json(
    f"{BASE_URL}/rest/workspaces.json"
)

workspace_items = as_list(
    (
        workspace_doc.get("workspaces")
        or {}
    ).get("workspace")
)

workspaces = []

for item in workspace_items:

    if isinstance(item, dict):
        name = item.get("name")
    else:
        name = str(item)

    if name:
        workspaces.append(name)


workspaces = sorted(
    set(workspaces),
    key=str.lower,
)


print(
    f"Found {len(workspaces)} workspace(s)",
    file=sys.stderr,
)


# ============================================================
# Enumerate every style in GeoServer
# ============================================================

# Key:
#
#   (scope, style_name)
#
# Value:
#
#   style_href

catalog_styles = {}


def add_style_listing(scope, listing):

    items = as_list(
        (
            listing.get("styles")
            or {}
        ).get("style")
    )

    for item in items:

        if isinstance(item, dict):

            name = (
                item.get("name")
                or ""
            ).strip()

            href = (
                item.get("href")
                or ""
            ).strip()

        else:

            name = str(item).strip()
            href = ""


        if not name:
            continue


        key = (
            scope,
            name,
        )


        if not href:

            if scope == "global":

                href = (
                    f"{BASE_URL}/rest/styles/"
                    f"{quote(name, safe='')}.json"
                )

            else:

                href = (
                    f"{BASE_URL}/rest/workspaces/"
                    f"{quote(scope, safe='')}/styles/"
                    f"{quote(name, safe='')}.json"
                )


        catalog_styles[key] = href


# ------------------------------------------------------------
# Global styles
# ------------------------------------------------------------

print(
    "Retrieving global styles...",
    file=sys.stderr,
)

try:

    global_listing = get_json(
        f"{BASE_URL}/rest/styles.json"
    )

    add_style_listing(
        "global",
        global_listing,
    )

except Exception as e:

    print(
        f"ERROR retrieving global styles: {e}",
        file=sys.stderr,
    )


# ------------------------------------------------------------
# Workspace styles
# ------------------------------------------------------------

for workspace in workspaces:

    print(
        f"Retrieving styles for workspace: {workspace}",
        file=sys.stderr,
    )

    url = (
        f"{BASE_URL}/rest/workspaces/"
        f"{quote(workspace, safe='')}"
        f"/styles.json"
    )

    try:

        listing = get_json(url)

        add_style_listing(
            workspace,
            listing,
        )

    except HTTPError as e:

        if e.code == 404:
            continue

        print(
            f"WARNING: workspace {workspace}: {e}",
            file=sys.stderr,
        )

    except Exception as e:

        print(
            f"WARNING: workspace {workspace}: {e}",
            file=sys.stderr,
        )


# ============================================================
# Include referenced styles that somehow were absent from
# catalog listings, provided that an href was captured.
# ============================================================

for key, info in usage.items():

    if key in catalog_styles:
        continue

    hrefs = sorted(
        info["hrefs"]
    )

    if hrefs:

        catalog_styles[key] = hrefs[0]

        print(
            "WARNING: style referenced by a layer was not "
            f"in style listing; adding from href: "
            f"{key[0]}:{key[1]}",
            file=sys.stderr,
        )


# ============================================================
# Resolve usage records that lacked a scope
# ============================================================

styles_by_name = defaultdict(list)

for key in catalog_styles:
    styles_by_name[key[1]].append(key)


still_unresolved = []

for item in unresolved_usage:

    candidates = styles_by_name.get(
        item["name"],
        [],
    )

    if len(candidates) == 1:

        key = candidates[0]

        usage[key]["layers"].add(
            item["layer"]
        )

        usage[key]["roles"].add(
            item["role"]
        )

        if item["href"]:
            usage[key]["hrefs"].add(
                item["href"]
            )

    else:

        still_unresolved.append(
            item
        )


unresolved_usage = still_unresolved


print()
print(
    f"Catalog styles discovered: {len(catalog_styles)}",
    file=sys.stderr,
)


# ============================================================
# Export styles
# ============================================================

manifest_rows = []

success_count = 0
error_count = 0


for (
    scope,
    style_name,
), style_href in sorted(
    catalog_styles.items(),
    key=lambda item: (
        item[0][0].lower(),
        item[0][1].lower(),
    ),
):

    print(
        f"Exporting [{scope}] {style_name}",
        file=sys.stderr,
    )


    status = "ok"
    error = ""

    style_format = ""
    filename = ""
    language_version = ""
    content_type = ""
    retrieval_method = ""

    body_relative = ""
    metadata_relative = ""


    try:

        # ----------------------------------------------------
        # Style metadata
        # ----------------------------------------------------

        meta_url = metadata_url(
            style_href
        )

        meta_doc = get_json(
            meta_url
        )

        meta = (
            meta_doc.get("style")
            or {}
        )


        style_format = (
            meta.get("format")
            or ""
        )

        filename = (
            meta.get("filename")
            or ""
        )

        language_version_obj = (
            meta.get("languageVersion")
            or {}
        )

        if isinstance(
            language_version_obj,
            dict,
        ):

            language_version = (
                language_version_obj.get(
                    "version"
                )
                or ""
            )

        else:

            language_version = str(
                language_version_obj
            )


        # ----------------------------------------------------
        # Scope directories
        # ----------------------------------------------------

        safe_scope = safe_name(
            scope
        )

        safe_style = safe_name(
            style_name
        )


        style_scope_dir = os.path.join(
            STYLES_DIR,
            safe_scope,
        )

        metadata_scope_dir = os.path.join(
            METADATA_DIR,
            safe_scope,
        )

        os.makedirs(
            style_scope_dir,
            exist_ok=True,
        )

        os.makedirs(
            metadata_scope_dir,
            exist_ok=True,
        )


        # ----------------------------------------------------
        # Save GeoServer style metadata
        # ----------------------------------------------------

        metadata_file = os.path.join(
            metadata_scope_dir,
            safe_style + ".json",
        )

        with open(
            metadata_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                meta_doc,
                f,
                ensure_ascii=False,
                indent=2,
            )

            f.write("\n")


        metadata_relative = os.path.relpath(
            metadata_file,
            EXPORT_DIR,
        )


        # ----------------------------------------------------
        # Determine local style file extension
        # ----------------------------------------------------

        ext = extension_from_filename(
            filename
        )

        if not ext:
            ext = default_extension(
                style_format
            )


        # Use GeoServer style name as local basename.
        #
        # The original GeoServer filename is kept in the
        # manifest and metadata JSON.
        body_file = os.path.join(
            style_scope_dir,
            safe_style + ext,
        )


        # ----------------------------------------------------
        # Retrieve exact/native style body
        # ----------------------------------------------------

        (
            body,
            content_type,
            retrieval_method,
        ) = download_native_style(
            style_href=style_href,
            style_format=style_format,
            filename=filename,
            language_version=language_version,
        )


        with open(
            body_file,
            "wb",
        ) as f:

            f.write(body)


        body_relative = os.path.relpath(
            body_file,
            EXPORT_DIR,
        )


        success_count += 1


    except HTTPError as e:

        status = "error"

        error = (
            f"HTTP {e.code}: {e.reason}"
        )

        error_count += 1

        print(
            f"  ERROR: {error}",
            file=sys.stderr,
        )


    except URLError as e:

        status = "error"

        error = str(
            e.reason
        )

        error_count += 1

        print(
            f"  ERROR: {error}",
            file=sys.stderr,
        )


    except Exception as e:

        status = "error"

        error = str(e)

        error_count += 1

        print(
            f"  ERROR: {error}",
            file=sys.stderr,
        )


    # --------------------------------------------------------
    # Layer usage
    # --------------------------------------------------------

    key = (
        scope,
        style_name,
    )

    info = usage.get(
        key,
        {
            "layers": set(),
            "roles": set(),
        },
    )

    layers = sorted(
        info["layers"]
    )

    roles = sorted(
        info["roles"]
    )


    manifest_rows.append({

        "style_name": style_name,

        "style_scope": scope,

        "style_format": style_format,

        "language_version": language_version,

        "original_filename": filename,

        "style_file": body_relative,

        "metadata_file": metadata_relative,

        "content_type": content_type,

        "retrieval_method": retrieval_method,

        "referenced_by_layer": (
            "yes"
            if layers
            else "no"
        ),

        "roles": "; ".join(
            roles
        ),

        "layers": "; ".join(
            layers
        ),

        "status": status,

        "error": error,
    })


# ============================================================
# Write manifest
# ============================================================

manifest_fields = [
    "style_name",
    "style_scope",
    "style_format",
    "language_version",
    "original_filename",
    "style_file",
    "metadata_file",
    "content_type",
    "retrieval_method",
    "referenced_by_layer",
    "roles",
    "layers",
    "status",
    "error",
]


with open(
    MANIFEST,
    "w",
    newline="",
    encoding="utf-8",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=manifest_fields,
    )

    writer.writeheader()

    writer.writerows(
        manifest_rows
    )


# ============================================================
# Report unresolved layer -> style associations
# ============================================================

UNRESOLVED_FILE = os.path.join(
    EXPORT_DIR,
    "unresolved_style_usage.csv",
)


if unresolved_usage:

    with open(
        UNRESOLVED_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "layer",
                "role",
                "name",
                "href",
            ],
        )

        writer.writeheader()

        writer.writerows(
            unresolved_usage
        )


# ============================================================
# Final summary
# ============================================================

referenced_count = sum(
    1
    for row in manifest_rows
    if row["referenced_by_layer"] == "yes"
)


print()
print("============================================")
print("GeoServer style export complete")
print("============================================")
print()
print(f"Export directory       : {EXPORT_DIR}")
print(f"Styles discovered      : {len(catalog_styles)}")
print(f"Styles exported        : {success_count}")
print(f"Style export errors    : {error_count}")
print(f"Styles used by layers  : {referenced_count}")
print(f"Unresolved associations: {len(unresolved_usage)}")
print(f"Manifest               : {MANIFEST}")

if unresolved_usage:
    print(
        f"Unresolved usage file  : {UNRESOLVED_FILE}"
    )

