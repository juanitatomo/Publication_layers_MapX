# MapX metadata QA notes
- Total JSON written: **79**
- ready: 58
- no_mapx_id: 18
- wrong_layer_warn: 2
- needs_review: 1

## wrong_layer (do not paste into wrong MapX view)
- `ESA2005_Cauc` → catalog mapx_id `MX-I4VTO-9X4S1-VQQPE` (WMS requested ESA2000_Cauc; title implies ESA2005_Cauc)
- `ESA2010_Cauc` → catalog mapx_id `MX-2FANI-UZZD6-QHA6V` (WMS requested ESA2000_Cauc; title implies ESA2010_Cauc)

## no_mapx_id
- `elevation_caucasus` (raster)
- `gmba_thermal` (raster)
- `k1_kapos` (raster)
- `k1k2k3_matrix` (raster)
- `k2_gmba_thermal` (raster)
- `k3_elu_lf` (raster)
- `ls_risk_cauc` (raster)
- `Caucasus_Ecocorridors_WGS84` (vector)
- `Priority_Conservation_Areas_WGS84` (vector)
- `WDPA_Caucasus` (vector)
- `caucasus_ecoregion_forest_cover` (vector)
- `caucasus_ecoregion_land_cover` (vector)
- `caucasus_ecoregion_wgs84_new` (vector)
- `emerald_2020_epsg4326_caucasus` (vector)
- `fires_2020` (vector)
- `leopard_distribution_area_wgs84` (vector)
- `railroads` (vector)
- `roads_caucasus_select` (vector)

## needs_review (weak/missing GeoNode abstract)
- `sum_of_average_daily_air_temperatures_above__10c`

## ID integrity
- Every `mapx_id` in `_metadata_index.csv` is copied verbatim from `triage/publication_catalog.csv` for the same `geonode_name`.
- No MX- identifiers were invented.
