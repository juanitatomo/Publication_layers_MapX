# Sustainable Caucasus GeoNode / GeoServer Data Inventory and Extraction

This document summarizes the inspection, backup, extraction, and migration of raster, vector, database, and GeoServer metadata from the Sustainable Caucasus GeoNode deployment.

The objective is to preserve enough information and source data to reproduce the published datasets and their cartographic configuration in MapX.

---

# 1. Connect to the VM

Connect to the remote VM using the configured SSH host:

```bash
ssh sustainable-caucasus
```

The GeoNode deployment is located under:

```bash
cd /opt/geonode/sustainable_caucasus4
```

---

# 2. Inspect the Dockerized GeoNode Instance

Inspect the Docker Compose configuration:

```bash
cd /opt/geonode/sustainable_caucasus4
cat docker-compose.yml
```

The configuration indicates where the GeoServer data directory is physically stored on the host:

```yaml
geoserver-data-dir:
  name: ${COMPOSE_PROJECT_NAME}-gsdatadir
  driver: local
  driver_opts:
    o: bind
    type: none
    device: /data/geonode/geoserver_data/data
```

Therefore, the GeoServer data directory is bound to:

```text
/data/geonode/geoserver_data/data
```

---

# 3. GeoServer GeoTIFF Data

## 3.1 Locate the GeoTIFF directory

The GeoTIFF resources published by GeoServer are stored under:

```bash
cd /data/geonode/geoserver_data/data/data/geonode
```

### Directory size

```bash
du -h --max-depth=0 .
```

Output:

```text
1.9G    .
```

The directory therefore contains approximately **1.9 GB** of data.

---

## 3.2 Count GeoTIFF files by extension

To recursively count the different TIFF/GeoTIFF extensions:

```bash
find . -type f | awk '
BEGIN {
  IGNORECASE=1
}
{
  if ($0 ~ /\.geotiff$/) geotiff++
  else if ($0 ~ /\.geotif$/) geotif++
  else if ($0 ~ /\.tiff$/) tiff++
  else if ($0 ~ /\.tif$/) tif++
}
END {
  print "geotiff:", geotiff+0
  print "geotif :", geotif+0
  print "tiff   :", tiff+0
  print "tif    :", tif+0
}'
```

Output:

```text
geotiff: 49
geotif : 0
tiff   : 0
tif    : 0
```

There are therefore **49 `.geotiff` files**.

The files are generally organized in separate directories, with approximately one GeoTIFF per directory.

---

## 3.3 List the GeoTIFF files

```bash
find . -type f -iname '*.geotiff'
```

Output:

```text
./caucasus_2017232_terra_250m/caucasus_2017232_terra_250m.geotiff
./caucasus_2017234_terra_250m/caucasus_2017234_terra_250m.geotiff
./dem_90_bs/dem_90_bs.geotiff
./caucasus_ecoregion_land_cover_tif/caucasus_ecoregion_land_cover_tif.geotiff
./caucasus_2017232_aqua_250m/caucasus_2017232_aqua_250m.geotiff
./n37_40_2000lc030/n37_40_2000lc030.geotiff
./caucasus_2017236_aqua_721_250m/caucasus_2017236_aqua_721_250m.geotiff
./seismic_hazard_armena/seismic_hazard_armena.geotiff
./caucasus_2017235_terra_721_250m/caucasus_2017235_terra_721_250m.geotiff
./caucasus_2017233_terra_721_250m/caucasus_2017233_terra_721_250m.geotiff
./azerbaijan_2017234_terra_250m/azerbaijan_2017234_terra_250m.geotiff
./s2_20170823/s2_20170823.geotiff
./caucasus_2017236_aqua_250m/caucasus_2017236_aqua_250m.geotiff
./azerbaijan_2017235_terra_250m/azerbaijan_2017235_terra_250m.geotiff
./caucasus_2017233_aqua_250m/caucasus_2017233_aqua_250m.geotiff
./azerbaijan_2017233_aqua_721_250m/azerbaijan_2017233_aqua_721_250m.geotiff
./caucasus_2000lc30m_gcs_wgs/caucasus_2000lc30m_gcs_wgs.geotiff
./_20170823_s2/_20170823_s2.geotiff
./gmba_thermal/gmba_thermal.geotiff
./caucasus_2017233_aqua_721_250m/caucasus_2017233_aqua_721_250m.geotiff
./n38_40_2000lc030/n38_40_2000lc030.geotiff
./_111/_111.geotiff
./caucasus_2017235_aqua_721_250m/caucasus_2017235_aqua_721_250m.geotiff
./azerbaijan_2017235_terra_721_250m/azerbaijan_2017235_terra_721_250m.geotiff
./dem_200_000/dem_200_000.geotiff
./caucasus_2017234_aqua_721_250m/caucasus_2017234_aqua_721_250m.geotiff
./caucasus_2017232_aqua_721_250m/caucasus_2017232_aqua_721_250m.geotiff
./azerbaijan_2017234_aqua_250m/azerbaijan_2017234_aqua_250m.geotiff
./azerbaijan_2017234_aqua_721_250m/azerbaijan_2017234_aqua_721_250m.geotiff
./tree_cover/tree_cover.geotiff
./caucasus_ecoregion_forest_cover_tif/caucasus_ecoregion_forest_cover_tif.geotiff
./co2_2010/co2_2010.geotiff
./caucasus_2017235_aqua_250m/caucasus_2017235_aqua_250m.geotiff
./n37_40_2010lc030/n37_40_2010lc030.geotiff
./caucasus_2017234_aqua_250m/caucasus_2017234_aqua_250m.geotiff
./k1k2k3_matrix/k1k2k3_matrix.geotiff
./k2_gmba_thermal/k2_gmba_thermal.geotiff
./caucasus_2017235_terra_250m/caucasus_2017235_terra_250m.geotiff
./caucasus_2017236_terra_250m/caucasus_2017236_terra_250m.geotiff
./k3_elu_lf/k3_elu_lf.geotiff
./caucasus_2017236_terra_721_250m/caucasus_2017236_terra_721_250m.geotiff
./caucasus_2017233_terra_250m/caucasus_2017233_terra_250m.geotiff
./seismic_hazard_armenia/seismic_hazard_armenia.geotiff
./k1_kapos/k1_kapos.geotiff
./n38_40_2010lc030/n38_40_2010lc030.geotiff
./caucasus_2017234_terra_721_250m/caucasus_2017234_terra_721_250m.geotiff
./seismic_hazard_475/seismic_hazard_475.geotiff
./Forest_height_2019_NAFR_Caucasus_Ecoregion/Forest_height_2019_NAFR_Caucasus_Ecoregion.geotiff
./caucasus_2017232_terra_721_250m/caucasus_2017232_terra_721_250m.geotiff
```

---

## 3.4 Inventory all file extensions

To identify the other file types present in the directory:

```bash
find . -type f \
  | awk -F. 'NF>1 {print tolower($NF)}' \
  | sort \
  | uniq -c \
  | sort -nr
```

Output:

```text
142 sh
 49 geotiff
  1 xml
  1 shx
  1 shp
  1 prj
  1 dbf
```

The numerous shell scripts appear to document or implement optimization and preprocessing operations applied to individual raster datasets.

---

## 3.5 Shapefile present in the GeoServer data directory

There is one Shapefile dataset.

Locate it with:

```bash
find . -type f -iname '*.shp'
```

Output:

```text
./rd_line/rd_line.shp
```

Associated `.dbf`, `.shx`, and `.prj` files are also present.

---

## 3.6 Retrieve the GeoServer data locally

From the local machine:

```bash
rsync -avhP \
  sustainable-caucasus:/data/geonode/geoserver_data/data/data/geonode/ \
  .
```

The trailing `/` on the source means that the **contents of the `geonode` directory** are copied into the current local directory.

---

# 4. GeoNode Importer Data

GeoNode also maintains an importer working directory containing raster and vector source files.

## 4.1 Locate the importer directory

```bash
cd /data/geonode/geoserver_data/data/geonode/importer_data
```

### Directory size

```bash
du -h --max-depth=0 .
```

Output:

```text
7.9G    .
```

The importer directory therefore contains approximately **7.9 GB** of data.

---

## 4.2 Count raster files

```bash
find . -type f | awk '
BEGIN {
  IGNORECASE=1
}
{
  if ($0 ~ /\.geotiff$/) geotiff++
  else if ($0 ~ /\.geotif$/) geotif++
  else if ($0 ~ /\.tiff$/) tiff++
  else if ($0 ~ /\.tif$/) tif++
}
END {
  print "geotiff:", geotiff+0
  print "geotif :", geotif+0
  print "tiff   :", tiff+0
  print "tif    :", tif+0
}'
```

Output:

```text
geotiff: 0
geotif : 0
tiff   : 0
tif    : 15
```

There are **15 `.tif` files**.

As with the GeoServer data directory, these files are generally organized into separate temporary directories.

---

## 4.3 List TIFF files

```bash
find . -type f -iname '*.tif'
```

Output:

```text
./tmp14013381083344953845/relief_san_andres.tif
./tmp4776300122479496232/Forest_height_2019_NAFR_Caucasus_Ecoregion.tif
./tmp2040843599610706580/wc2.1_30s_elev_clipped.tif
./tmp8990254255304039989/elevation_caucasus.tif
./tmp5842988287151057960/GHS_2015.tif
./tmp4126359404649560310/The_Mountainous_Shirvan.tif
./tmp5829399476221404509/ESA2010_Cauc.tif
./tmp4184135837943550819/ESA2005_Cauc.tif
./tmp6601272676805775000/ls_risk_cauc.tif
./tmp3974991336699186319/biomes_caucasus_clip.tif
./tmp2937055102632715858/Forest_height_2019_NAFR_Caucasus_Ecoregion.tif
./tmp6682973757159128818/ESA2000_Cauc.tif
./tmp8189966123792810504/elevation_caucasus.tif
./tmp4444953639116415706/wc2.1_30s_elev_clipped.tif
./tmp2246077771405314819/Forest_height_2019_NAFR_Caucasus_Ecoregion.tif
```

Some datasets appear multiple times in different temporary importer directories.

---

## 4.4 Inventory all file extensions

```bash
find . -type f \
  | awk -F. 'NF>1 {print tolower($NF)}' \
  | sort \
  | uniq -c \
  | sort -nr
```

Output:

```text
25 locking
15 tif
 7 shx
 7 shp
 7 prj
 7 dbf
 3 jpg
 1 /geonode_initialized
```

The importer directory contains:

- 15 TIFF raster files
- 7 Shapefile instances
- 3 JPEG files
- several importer locking/state files

---

## 4.5 List Shapefiles

```bash
find . -type f -iname '*.shp'
```

Output:

```text
./tmp5281942420286831965/City.shp
./tmp8350306800993318228/Rivers.shp
./tmp8576999934243811721/City.shp
./tmp6864008537227202195/GWSP_Caucasus.shp
./tmp5003323485428208426/City.shp
./tmp4790825849921617881/City.shp
./tmp6823197357460010257/City.shp
```

There are **7 Shapefile instances**, although several appear to be repeated copies of `City.shp`.

---

## 4.6 Retrieve the importer data locally

Because the directory may contain files with ownership or permission constraints, first copy it to the user's home directory on the VM:

```bash
cp -r \
  /data/geonode/geoserver_data/data/geonode/importer_data \
  /home/thomas/
```

Change ownership:

```bash
cd /home/thomas/

chown -R thomas:thomas importer_data
```

Then retrieve it from the local machine:

```bash
rsync -avhP \
  sustainable-caucasus:/home/thomas/importer_data \
  .
```

---

# 5. PostGIS Database

GeoServer vector layers are primarily stored in the GeoNode PostGIS database.

## 5.1 Identify the PostgreSQL container

From the VM:

```bash
cd /opt/geonode/sustainable_caucasus4
```

Identify the database container:

```bash
CONTAINER_GN=$(docker ps -q -f "name=db4sustainable_caucasus4")
```

Set the GeoDatabase name:

```bash
DBNAME2=sustainable_caucasus4_data
```

Open an interactive PostgreSQL session:

```bash
docker exec -it "$CONTAINER_GN" \
  psql -U postgres "$DBNAME2"
```

Observed PostgreSQL version:

```text
psql (13.2)
Type "help" for help.
```

---

## 5.2 List database schemas

Inside `psql`:

```sql
\dn
```

Output:

```text
List of schemas
 Name  |  Owner
-------+----------
 public | postgres
(1 row)
```

The spatial data is stored in the `public` schema.

---

## 5.3 List all tables

```sql
\dt
```

Example output:

```text
                                               List of relations
 Schema |                              Name                               | Type  |           Owner
--------+-----------------------------------------------------------------+-------+----------------------------
 public | Caucasus_Ecocorridors_WGS84                                     | table | sustainable_caucasus4_data
 public | Centre_of_regions                                               | table | sustainable_caucasus4_data
 public | Centre_of_regions0                                              | table | sustainable_caucasus4_data
 public | City0                                                           | table | sustainable_caucasus4_data
 public | City1                                                           | table | sustainable_caucasus4_data
 ...
 public | vegetation_arm                                                  | table | sustainable_caucasus4_data
 public | water_channels_in_azerbaijan                                    | table | sustainable_caucasus4_data
 public | wdpa_caucasus                                                   | table | sustainable_caucasus4_data
 public | wind_resources                                                  | table | sustainable_caucasus4_data
(157 rows)
```

The database contains **157 tables**.

---

## 5.4 List spatial tables

To list tables registered in PostGIS `geometry_columns`:

```sql
SELECT DISTINCT f_table_name
FROM geometry_columns
WHERE f_table_schema = 'public'
ORDER BY f_table_name;
```

Example output:

```text
                         f_table_name
-----------------------------------------------------------------
 Caucasus_Ecocorridors_WGS84
 Centre_of_regions
 Centre_of_regions0
 City0
 ...
 wdpa_caucasus
 wind_resources
(142 rows)
```

There are **142 spatial tables** registered in PostGIS.

This implies that most of the 157 database tables contain geospatial vector data.

---

# 6. PostgreSQL Backup

A daily compressed SQL dump is available at:

```text
/var/backups/postgres/dump_sustainable_caucasus4_data.sql.gz
```

Retrieve it locally with:

```bash
rsync -avhP \
  sustainable-caucasus:/var/backups/postgres/dump_sustainable_caucasus4_data.sql.gz \
  .
```

This dump provides a database-level backup of the GeoNode spatial database.

---

# 7. GeoServer Layer Metadata

GeoServer's REST API is used to retrieve the configuration and metadata required to reconstruct the published layers.

The inventory script enumerates GeoServer workspaces and layers and extracts metadata such as:

- workspace
- layer name
- qualified layer name
- title
- abstract
- description
- keywords
- layer/resource type
- native resource name
- CRS
- native and geographic bounding boxes
- geometry column
- geometry type
- attribute schema
- default style
- alternate styles
- store name
- store type
- PostGIS schema/table
- source file path for file-backed datasets
- raster coverage metadata
- GeoServer metadata
- WMS layer name

---

## 7.1 Enter the GeoServer container

Identify the relevant container if necessary:

```bash
docker ps
```

Enter the GeoServer container:

```bash
docker exec -it 7c6f102df066 /bin/bash
```

> The container ID is deployment-specific and may change after a restart. Using the container name is preferable where possible.

---

## 7.2 Run the GeoServer inventory script

From inside the GeoServer container:

```bash
python3 /tmp/geoserver_inventory.py
```

The current version generates:

```text
/tmp/geoserver_layers_all_workspaces.csv
```

The CSV contains one row per published GeoServer layer, including its workspace and associated source/store metadata.

---

# 8. GeoServer Style Export

GeoServer styles are exported in their original/native representation where possible.

The export process retrieves:

- global GeoServer styles
- workspace-specific styles
- default layer styles
- alternate layer styles
- style format
- style language version
- original filename
- style metadata
- layer/style associations

Supported native style formats may include:

- SLD
- SE
- GeoCSS/CSS
- YSLD
- Mapbox Style / MBStyle

---

## 8.1 Run the style export script

From inside the GeoServer container:

```bash
python3 /tmp/export_geoserver_styles.py
```

The export is stored under:

```text
/tmp/geoserver_export/
```

The expected structure is similar to:

```text
/tmp/geoserver_export/
├── geoserver_layers_all_workspaces.csv
├── style_manifest.csv
├── styles/
│   ├── global/
│   ├── geonode/
│   └── <other_workspaces>/
└── style_metadata/
    ├── global/
    ├── geonode/
    └── <other_workspaces>/
```

The `style_manifest.csv` associates each exported style with:

- style name
- GeoServer scope/workspace
- style format
- style language version
- original filename
- exported style file
- metadata file
- layers using the style
- whether the style is used as a default or alternate style
- export status

---

# 9. Restore the PostGIS Dump Locally with Docker

The PostgreSQL dump can be restored into a temporary local PostGIS instance for inspection and export.

This avoids installing PostgreSQL/PostGIS directly on the local machine.

The source system uses PostgreSQL **13.2**, so a PostgreSQL 13/PostGIS image is preferred for compatibility.

On Apple Silicon Macs, the official PostGIS image may need to run under `linux/amd64` emulation.

---

## 9.1 Start the temporary PostGIS container

```bash
docker run -d \
  --platform linux/amd64 \
  --name sc-postgis \
  -e POSTGRES_PASSWORD='TEMP_PASSWORD' \
  -e POSTGRES_DB='sustainable_caucasus4_data' \
  -p 127.0.0.1:55432:5432 \
  -v sc-postgis-data:/var/lib/postgresql/data \
  postgis/postgis:13-3.5
```

The PostgreSQL instance is exposed only on the local machine:

```text
Host:     127.0.0.1
Port:     55432
Database: sustainable_caucasus4_data
User:     postgres
Password: TEMP_PASSWORD
```

Binding the Docker port to:

```text
127.0.0.1:55432
```

means the temporary database is accessible from the local machine but is not exposed on external network interfaces.

---

## 9.2 Check that PostgreSQL is ready

```bash
docker exec sc-postgis pg_isready -U postgres
```

Expected output:

```text
/var/run/postgresql:5432 - accepting connections
```

---

## 9.3 Create roles referenced by the original dump

The source database contains objects owned by:

```text
sustainable_caucasus4_data
```

and potentially:

```text
sustainable_caucasus4
```

Create those roles before importing the dump:

```bash
docker exec -i sc-postgis \
  psql -U postgres -d postgres <<'SQL'
CREATE ROLE sustainable_caucasus4_data;
CREATE ROLE sustainable_caucasus4;
SQL
```

Login privileges are not required for these roles in this temporary extraction environment.

---

## 9.4 Restore the compressed SQL dump

The compressed dump can be streamed directly into PostgreSQL without first extracting it to disk:

```bash
gzip -dc dump_sustainable_caucasus4_data.sql.gz \
  | docker exec -i sc-postgis \
      psql \
      -U postgres \
      -d sustainable_caucasus4_data
```

---

## 9.5 Verify the restored tables

List all tables:

```bash
docker exec -it sc-postgis \
  psql \
  -U postgres \
  -d sustainable_caucasus4_data \
  -c '\dt public.*'
```

List the spatial tables:

```bash
docker exec -it sc-postgis \
  psql \
  -U postgres \
  -d sustainable_caucasus4_data \
  -c "
SELECT
    f_table_schema,
    f_table_name,
    f_geometry_column,
    type,
    srid
FROM geometry_columns
WHERE f_table_schema = 'public'
ORDER BY f_table_name;
"
```

Approximately **142 spatial tables** are expected.

---

## 9.6 Connect from the local machine

If `psql` is installed locally:

```bash
PGPASSWORD='TEMP_PASSWORD' psql \
  -h 127.0.0.1 \
  -p 55432 \
  -U postgres \
  -d sustainable_caucasus4_data
```

The PostgreSQL server runs inside Docker, but can be used by tools installed directly on the local machine.

---

# 10. Export All Spatial PostGIS Tables to GeoPackage

The restored PostGIS database can be accessed directly by local GDAL/OGR tools.

The target structure is:

```text
PostGIS table
    ↓
one GeoPackage file
    ↓
one layer with the same name as the PostgreSQL table
```

For example:

```text
public.wdpa_caucasus
    ↓
wdpa_caucasus.gpkg
    ↓
layer: wdpa_caucasus
```

No reprojection is performed during this process.

The original CRS, geometries, and attribute data are retained.

---

## 10.1 Verify local GDAL PostgreSQL support

Check whether the local GDAL installation includes the PostgreSQL driver:

```bash
ogrinfo --formats | grep -i Postgre
```

Expected output should contain something similar to:

```text
PostgreSQL -vector- (rw+): PostgreSQL/PostGIS
```

---

## 10.2 Test the PostGIS connection with OGR

```bash
PGPASSWORD='TEMP_PASSWORD' ogrinfo \
  "PG:host=127.0.0.1 port=55432 dbname=sustainable_caucasus4_data user=postgres"
```

This should list the available PostGIS layers.

---

## 10.3 Test one table before exporting everything

It is recommended to test the process on a single table first:

```bash
PGPASSWORD='TEMP_PASSWORD' ogr2ogr \
  -f GPKG \
  test_wdpa.gpkg \
  "PG:host=127.0.0.1 port=55432 dbname=sustainable_caucasus4_data user=postgres" \
  "public.wdpa_caucasus" \
  -nln "wdpa_caucasus" \
  -overwrite \
  -progress
```

Inspect the resulting layer:

```bash
ogrinfo -so test_wdpa.gpkg wdpa_caucasus
```

---

## 10.4 Export all spatial tables

Create an output directory:

```bash
mkdir -p gpkg
```

Then export every table registered in `geometry_columns`:

```bash
DB_PASSWORD='TEMP_PASSWORD'
DB_HOST='127.0.0.1'
DB_PORT='55432'
DB_NAME='sustainable_caucasus4_data'
DB_USER='postgres'
DB_SCHEMA='public'

OUTDIR="$PWD/gpkg"

mkdir -p "$OUTDIR"

PGPASSWORD="$DB_PASSWORD" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -AtF $'\t' \
  -c "
SELECT DISTINCT
    f_table_schema,
    f_table_name
FROM geometry_columns
WHERE f_table_schema = '${DB_SCHEMA}'
ORDER BY f_table_schema, f_table_name;
" |
while IFS=$'\t' read -r schema table; do

    echo "Exporting ${schema}.${table}"
    echo "  -> ${OUTDIR}/${table}.gpkg"

    PGPASSWORD="$DB_PASSWORD" ogr2ogr \
      -f GPKG \
      "${OUTDIR}/${table}.gpkg" \
      "PG:host=${DB_HOST} port=${DB_PORT} dbname=${DB_NAME} user=${DB_USER}" \
      "${schema}.${table}" \
      -nln "$table" \
      -overwrite \
      -progress

    if [ $? -ne 0 ]; then
        echo "ERROR exporting ${schema}.${table}" >&2
    fi

done

unset DB_PASSWORD
```

This produces a directory similar to:

```text
gpkg/
├── Caucasus_Ecocorridors_WGS84.gpkg
├── Centre_of_regions.gpkg
├── Centre_of_regions0.gpkg
├── City0.gpkg
├── wdpa_caucasus.gpkg
├── wind_resources.gpkg
└── ...
```

Each `.gpkg` contains one layer whose name matches the source PostgreSQL table.

---

## 10.5 Count the exported GeoPackages

```bash
find gpkg -type f -name '*.gpkg' | wc -l
```

Based on the source database inventory, approximately:

```text
142
```

GeoPackages are expected.

---

## 10.6 Check for empty output files

```bash
find gpkg \
  -type f \
  -name '*.gpkg' \
  -size 0 \
  -print
```

No output indicates that no zero-byte GeoPackages were produced.

---

## 10.7 Validate all GeoPackages

To verify that every generated GeoPackage can be opened by GDAL:

```bash
for f in gpkg/*.gpkg; do
    if ! ogrinfo "$f" >/dev/null 2>&1; then
        echo "INVALID: $f"
    fi
done
```

If nothing is printed, all GeoPackages could be opened successfully.

---

## 10.8 Preservation considerations

The original PostgreSQL dump should be retained even after all GeoPackages have been exported.

Recommended migration archive:

```text
migration/
├── dump_sustainable_caucasus4_data.sql.gz
├── gpkg/
├── geoserver_layers_all_workspaces.csv
├── geoserver_export/
├── geoserver_rasters/
└── geonode_importer_data/
```

The PostgreSQL dump remains the authoritative database backup because GeoPackage does not preserve all PostgreSQL-specific objects, such as:

- PostgreSQL indexes
- triggers
- constraints
- sequences
- views
- ownership
- database privileges
- PostgreSQL-specific column types
- database functions

The GeoPackages should therefore be considered migration/interchange datasets rather than full database backups.

---

# 11. Remove the Temporary PostGIS Environment

Once all exported data has been validated, stop the temporary container:

```bash
docker stop sc-postgis
```

Remove it:

```bash
docker rm sc-postgis
```

If the restored PostgreSQL database is no longer required, also remove the Docker volume:

```bash
docker volume rm sc-postgis-data
```

Do this only after verifying that the SQL dump and exported GeoPackages are safely stored.

---

# 12. Data Inventory Summary

The current inspection identified the following main data sources.

| Source | Content | Observed quantity |
|---|---|---:|
| GeoServer data directory | `.geotiff` rasters | 49 |
| GeoServer data directory | Shapefiles | 1 |
| GeoServer data directory | Shell processing scripts | 142 |
| GeoNode importer directory | `.tif` rasters | 15 |
| GeoNode importer directory | Shapefile instances | 7 |
| PostGIS `public` schema | All tables | 157 |
| PostGIS `geometry_columns` | Spatial tables | 142 |
| PostgreSQL backup | Compressed SQL dump | 1 |

Storage observed:

| Directory | Size |
|---|---:|
| `/data/geonode/geoserver_data/data/data/geonode` | 1.9 GB |
| `/data/geonode/geoserver_data/data/geonode/importer_data` | 7.9 GB |

---

# 13. Assets Required for Reproduction in MapX

For a faithful reconstruction of the existing GeoServer layers in MapX, the migration package should ideally preserve the following.

## Source data

### Vector

- PostGIS spatial tables exported as GeoPackage
- original Shapefiles where relevant
- geometry types
- attribute names and types
- coordinate reference systems
- original PostgreSQL dump as a database-level backup

### Raster

- original GeoTIFF/TIFF files
- coordinate reference systems
- raster extent
- nodata information
- raster dimensions and resolutions

---

## Metadata

Preserve:

- workspace
- layer name
- qualified layer name
- title
- abstract/description
- keywords
- CRS
- bounding box
- source/store information
- PostGIS table or source file
- metadata links where available
- attribute schema

---

## Cartography

Preserve:

- default GeoServer style
- alternate GeoServer styles
- original SLD/CSS/YSLD/MBStyle files
- external graphics referenced by styles
- classification rules
- colors and opacity
- line and polygon symbols
- labels
- scale-dependent rendering rules
- raster color maps

---

## Additional GeoServer configuration

Where relevant, preserve:

- layer groups
- layer ordering within groups
- WMS/WMTS configuration
- external/cascaded service URLs
- custom legends
- style graphic resources such as PNG or SVG symbols

These elements are required to reproduce not only the source datasets, but also the presentation and behavior of the existing GeoServer publication as accurately as possible in MapX.

---

# 14. Recommended Migration Package Structure

A practical final archive could use the following structure:

```text
sustainable_caucasus_migration/
├── database/
│   ├── dump_sustainable_caucasus4_data.sql.gz
│   └── gpkg/
│       ├── Caucasus_Ecocorridors_WGS84.gpkg
│       ├── wdpa_caucasus.gpkg
│       └── ...
│
├── geoserver/
│   ├── geoserver_layers_all_workspaces.csv
│   ├── style_manifest.csv
│   ├── styles/
│   │   ├── global/
│   │   ├── geonode/
│   │   └── ...
│   └── style_metadata/
│       ├── global/
│       ├── geonode/
│       └── ...
│
├── rasters/
│   ├── geoserver/
│   └── geonode_importer/
│
├── shapefiles/
│
└── README.md
```

This structure separates:

1. **authoritative database backups**
2. **portable vector datasets**
3. **original raster datasets**
4. **GeoServer publication metadata**
5. **GeoServer cartographic styles**
6. **migration documentation**

Together, these assets provide a strong basis for reconstructing the Sustainable Caucasus datasets and their publication configuration in MapX.