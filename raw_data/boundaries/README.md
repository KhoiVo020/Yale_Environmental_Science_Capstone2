# 2020 county boundaries

`study_counties_2020.geojson` contains Orange County (`06059`) and Riverside County (`06065`) from the Census Bureau's [2020 TIGER/Line county archive](https://www2.census.gov/geo/tiger/TIGER2020/COUNTY/tl_2020_us_county.zip), retrieved November 19, 2026. See [2020 TIGER/Line documentation](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2020.html).

The two features were selected by California state code `06` and county codes `059` and `065`. All source attributes were retained, geometry was not simplified, and NAD83 coordinates were transformed to WGS84 longitude/latitude for GeoJSON. Both geometries passed validity checks. Hashes and the selection are recorded in [source_metadata.json](source_metadata.json).

Use `GEOID` to join the population table. `ALAND` and `AWATER` are Census land and water area attributes in square meters; they are not measures of developed land. Before summarizing NLCD, transform the boundaries to the raster's actual equal-area coordinate system. Never calculate acres from longitude/latitude degrees.

The full national ZIP is about 77 MB and is not committed. The optional `scripts/0_prepare_boundaries.py` helper downloads/caches it and recreates this subset. Its metadata records the subset preparation date on each run. The initial source was downloaded on the date above.
