# MapX style paste guide

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

- Layers in guide: **66**
- Paste as categorical: **54**
- Range / partial (do not paste as categorical values): **8**
- GeoCSS skip: **4**

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
