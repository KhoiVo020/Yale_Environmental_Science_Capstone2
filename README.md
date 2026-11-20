# Land-cover change and population growth in Orange and Riverside Counties

Capstone project for the Yale Environmental Data Science Certificate.

## Project description

This project investigates how community expansion relates to changes in the surrounding landscapes of Orange and Riverside Counties, California. It combines land-cover maps with decennial population counts to describe development between 2000 and 2020. The analysis uses three observation years: **2000, 2010, and 2020**.

The work builds on identifying variable types, filtering observations, calculating new variables, summarizing groups, and making readable visualizations. It is a descriptive study: an association between population growth and land conversion would not, by itself, establish a causal relationship.

## Research questions

1. How much did developed land increase in each county between 2000 and 2020?
2. Which land-cover categories, such as shrubland, grassland, or agricultural land, most frequently changed into developed land?
3. How did the amount of developed land per resident change during this period?

Comparisons will cover 2000-2010, 2010-2020, and the full 2000-2020 period.

## Datasets

| Dataset | Role in the project | Current status |
| --- | --- | --- |
| [USGS Annual NLCD, Collection 1.2](https://www.usgs.gov/data/annual-national-land-cover-database-nlcd-collection-1-products) | Categorical, 30 m land-cover rasters for exactly 2000, 2010, and 2020 | Selected; raster download and analysis are the next stage |
| [U.S. Decennial Census county population](https://www.census.gov/library/visualizations/interactive/how-has-our-nations-population-changed.html) | Numeric population counts for the three census years | Downloaded and cleaned; six county-year observations included |
| [2020 Census TIGER/Line county boundaries](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2020.html) | Fixed county study areas; spatial joins using GEOID | Orange and Riverside boundary subset included |

The Census source combines 2000 SF1, 2010 SF1, and 2020 DHC data. The repository contains a California extract with all original demographic groups, plus the official county-code lookup. The cleaning script selects only **Total Population**. GEOIDs are text identifiers: **06059** for Orange and **06065** for Riverside.

Annual NLCD supports the exact requested years. The project will use all three layers from the same collection, rather than substitute legacy NLCD's 2001, 2011, or 2021 layers. Developed land means classes **21-24**, including developed open space; it is not the same as impervious surface area. Full source links, snapshot dates, and checksums are recorded in [raw_data/README.md](raw_data/README.md).

## What is complete for Prompt 2

The commented [population cleaning script](scripts/1_clean_population.R) runs on the included Census data and produces a six-row county-year table. It uses `filter()` to select the observations, `mutate()` to parse counts and calculate changes, and `group_by()` with `summarise()` to compare each county across time. It preserves leading zeros in GEOIDs, joins the official county identifiers, and checks missing values, duplicates, and year coverage.

The population summaries are reproducible outputs. **Land-cover areas, conversion totals, and developed land per resident have not yet been calculated.** The next stage is described in the [land-cover analysis plan](docs/land_cover_analysis_plan.md).

## Measuring land conversion

The conversion table will report both **acres converted** and **the percentage of each starting land-cover category converted**:

```text
percent_starting_class_converted = 100 * converted_acres / starting_acres
```

For example, shrubland may contribute the most converted acres because it occupied more land initially. Dividing by starting shrubland area shows the share of that category lost to development. The denominator is not the total area of all new development. A category with zero starting area receives a missing percentage, not zero percent.

Each table row will identify the county, start year, end year, starting category, starting acres, converted acres, and percentage converted. Matched raster cells are needed to identify transitions; differences between county-wide category totals cannot identify where new development came from. Gross conversion into development will be reported separately from the net change in developed area.

Developed land per resident will be calculated as `developed_acres / population` for each county and year, using the same 2020 county boundaries and a checked, common raster footprint.

## Repository contents

```text
raw_data/
  population/     California Census extract, county codes, source notes
  boundaries/     Two-county TIGER subset and provenance
  land_cover/     Instructions for the three Annual NLCD layers
clean_data/       Cleaned county population table
scripts/          Download helpers and commented R preprocessing
results/          Population growth tables and cleaning checks
figures/          Reserved for project charts and maps
docs/             Data dictionary, spatial analysis plan, discussion draft
```

## Run the population cleaning

Use R 4.1 or later and dplyr 1.1 or later. Install the two packages once in R:

```r
install.packages(c("dplyr", "readr"))
```

Then, from the repository folder:

```sh
Rscript scripts/1_clean_population.R
```

In RStudio, open [the project file](Yale_Environmental_Science_Capstone2.Rproj) and run `source("scripts/1_clean_population.R")`. The included source snapshots make cleaning possible without an API key or network connection after package installation. Rerunning replaces the generated population tables and report, while leaving the source files unchanged.

Validation used R 4.6.0 through WebR, dplyr 1.2.1, and readr 2.2.0. Checks covered the six source counts, missing observations, duplicate handling, and consistency after shuffling input rows.

Optional source-refresh helpers use Python. `python scripts/0_download_population.py` needs only the standard library. To recreate the boundary subset, first install `requirements.txt`, then run `python scripts/0_prepare_boundaries.py`. These helpers need internet access. The national TIGER archive is excluded from Git; the small two-county subset is included.

## Expected outputs and next steps

- Bar charts comparing developed acres by county and year.
- Maps showing mapped conversions into developed land.
- Conversion tables showing both acres and the share of each starting category converted.
- A line chart of developed acres per resident in 2000, 2010, and 2020.

Plots will use clear units, readable labels, and accessible colors. Before comparing rasters, check classification codes, grid alignment, coordinate systems, and missing coverage. Use a fixed 2020 boundary for land-cover summaries and check whether earlier Census geographies are compatible. Annual land classifications and Census Day population counts are not exactly simultaneous. Classification uncertainty, mixed pixels, and county-edge choices will be discussed when interpreting mapped changes.

## Assistance

The project idea and research questions were provided by the author. OpenAI Codex assisted with drafting documentation, and running checks.
