# Land-cover analysis plan

The population preprocessing and county boundary subset are available.
Land-cover rasters have not been acquired, and no conversion results are
claimed here. The next stage will use Python: Rasterio for raster data,
GeoPandas for county boundaries, NumPy for cell comparisons, pandas for
summary tables, and Matplotlib for charts and maps. Install those additional
analysis packages when beginning the raster work; the current requirements
cover population cleaning and boundary preparation.

Use **Annual NLCD Collection 1.2** land cover for exactly 2000, 2010, and
2020. Legacy NLCD years such as 2001 and 2011 are not substitutes.
[USGS product information](https://www.usgs.gov/centers/eros/science/annual-national-land-cover-database)
and the [user guide](https://www.usgs.gov/centers/eros/science/annual-nlcd-science-product-user-guide)
document the collection.

Transform the fixed 2020 TIGER/Line county polygons (`06059`, `06065`) into
the rasters' native CRS. Verify metadata, equal-area projection, 30 m cell
size, alignment, extent, and class codes. Use the same cell-center county
mask and cells valid in **all three years**. Report total county cells,
valid cells, excluded cells, and coverage percentage; investigate incomplete
coverage before comparing results. NoData 250 and missing cells are not zero.

Developed land comprises codes 21-24, including developed open space.
Keep shrub/scrub 52, grassland/herbaceous 71, pasture/hay 81, and crops 82
separate. If combining agriculture, sum acres and denominators before
calculating percentages; do not average class percentages.

Compare 2000-2010, 2010-2020, and 2000-2020 directly from each pair of
endpoints. Gross conversion counts cells starting nondeveloped and ending
developed. Net developed change is ending developed acres minus starting
developed acres. The twenty-year transition is not the sum of decade
transitions. Each conversion percentage uses its own starting class area
within common coverage as the denominator.
Endpoint comparisons cannot reveal temporary conversions that reverse
between observation years.

The following is an **illustrative calculation** for future transition counts;
it has not been run on the project's land-cover rasters. `pixels` must
include unchanged and changed cells.

```python
developed_codes = [21, 22, 23, 24]
nondeveloped = transitions.loc[
    ~transitions["from_code"].isin(developed_codes)
].copy()
nondeveloped["converted_pixels"] = nondeveloped["pixels"].where(
    nondeveloped["to_code"].isin(developed_codes), 0
)

# Include all destinations in starting area, but only development in conversion.
conversion = nondeveloped.groupby(
    ["geoid", "start_year", "end_year", "from_code"], as_index=False
).agg(
    starting_pixels=("pixels", "sum"),
    converted_pixels=("converted_pixels", "sum"),
)
acres_per_pixel = 900 / 4046.8564224
conversion["starting_acres"] = conversion["starting_pixels"] * acres_per_pixel
conversion["converted_acres"] = conversion["converted_pixels"] * acres_per_pixel

# A zero starting area has no defined conversion percentage; leave it missing.
starting_area = conversion["starting_acres"].where(conversion["starting_acres"] > 0)
conversion["percent_starting_class_converted"] = (
    100 * conversion["converted_acres"] / starting_area
)
```

The 900 square-meter factor applies only after verifying the native 30 m grid.
Report mapped change with classification uncertainty, and check population
geography compatibility. Descriptive comparisons cannot establish causation.
