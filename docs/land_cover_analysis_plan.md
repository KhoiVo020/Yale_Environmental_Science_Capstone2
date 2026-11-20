# Land-cover analysis plan

The population preprocessing and county boundary subset are available.
Land-cover rasters have not been acquired, and no conversion results are
claimed here. The next stage will use R packages `terra`, `sf`, and `dplyr`.

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

The following is an **illustrative, unexecuted** calculation on future
transition counts. `pixels` must include unchanged and changed cells.

```r
conversion <- transitions %>%
  filter(!from_code %in% 21:24) %>%
  group_by(geoid, start_year, end_year, from_code) %>%
  summarise(starting_pixels = sum(pixels),
            converted_pixels = sum(pixels[to_code %in% 21:24]),
            .groups = "drop") %>%
  mutate(starting_acres = starting_pixels * 900 / 4046.8564224,
         converted_acres = converted_pixels * 900 / 4046.8564224,
         percent_starting_class_converted =
           100 * converted_acres / na_if(starting_acres, 0))
```

The 900 square-meter factor applies only after verifying the native 30 m grid.
Report mapped change with classification uncertainty, and check population
geography compatibility. Descriptive comparisons cannot establish causation.
