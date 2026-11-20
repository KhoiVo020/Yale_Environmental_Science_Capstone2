# Land-cover inputs: next step

No rasters or calculated land-conversion results are included yet.

1. Open the [MRLC Viewer](https://www.mrlc.gov/viewer/) and select an area
   covering Orange and Riverside Counties. A bounding rectangle can include
   both counties; apply the exact county masks during processing.
2. Request Annual NLCD **Collection 1.2 Land Cover**, years **2000, 2010,
   2020**, as GeoTIFFs. Preserve native resolution and alignment; avoid
   resampling. The viewer delivers download instructions by email.
3. Save the downloaded layers here using project names
   `annual_nlcd_2000.tif`, `annual_nlcd_2010.tif`, and `annual_nlcd_2020.tif`.
   These are local naming choices, not promised provider filenames.
4. Retain metadata, download dates, original names, and checksums. Verify
   matching collection, CRS, grid, year, coverage, and categorical values
   before following the [analysis plan](../../docs/land_cover_analysis_plan.md).

[USGS access instructions](https://www.usgs.gov/centers/eros/science/annual-nlcd-data-access)
describe download options. Keep large source rasters outside Git history.
