# Population source notes

Retrieved: 2026-11-19 (local calendar date).

## County population

Provider: U.S. Census Bureau. The county CSV accompanies *How Has Our Nation's
Population Changed?*, published May 25, 2023.

- [Dataset page](https://www.census.gov/library/visualizations/interactive/how-has-our-nations-population-changed.html)
- [Original national CSV](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/population-pyramid-visualization/counties-populationpyramid-2000-2010-2020.csv)
- [Technical documentation](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/population-pyramid-visualization/population-changed-technical-documentation.pdf)

The documentation identifies the underlying sources as Census 2000 Summary
File 1 (SF1), 2010 Census Summary File 1 (SF1), and the 2020 Census Demographic
and Housing Characteristics File (DHC). `Population` is the count for the
specified `Group`, county, and census year. For this project, use only
`Group == "Total Population"`; the other groups overlap and must not be added
together. These are decennial census counts, not annual population estimates.

`ca_county_population_source.csv` is a California-only extract of the provider
file. The **only extraction filter** is `State == "California"`. All original
columns, groups, years, row order, and field values are preserved. The file is
decoded from the provider's Windows-1252 encoding and written as UTF-8 CSV
with LF line endings; CSV quoting may differ from the provider's file. No
population values are cleaned or calculated at this step.

- Extract rows, excluding header: 4,176
- Extract columns: 12
- National source bytes: 24,063,887
- National source SHA-256: `ddb44b14ede10563209f7cbb39c128c42c2e6c12c5398bc848a0381bc4dce7eb`
- California extract SHA-256: `4b57b25098bf0224569eaff54eae53737ac82c631612ae183aef6af776d1fd1b`

The full national CSV is downloaded into memory and is not stored in this
repository. The extract contains enough rows to practice filtering counties,
years, and population groups before preparing the six study observations.

## County identifiers

`national_county2020.txt` is the unchanged [2020 Census national county-code
file](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt), separated by `|`. Read `STATEFP` and `COUNTYFP` as
text, then concatenate them to make the five-character `GEOID`.

| County | State FIPS | County FIPS | GEOID |
| --- | --- | --- | --- |
| Orange County, California | 06 | 059 | 06059 |
| Riverside County, California | 06 | 065 | 06065 |

The population CSV has county and state names but no FIPS codes. Match both
state and county name to this lookup before linking the population table to
the 2020 TIGER/Line county boundaries.

- Original county-code file bytes: 126,639
- Original county-code file SHA-256: `9f6e5f6eb6ac2f5e9a36d5fd01dec77991bddc75118f748a069441a4782970d6`

## Refresh these inputs

From the repository root, run:

```sh
python scripts/0_download_population.py
```

The script uses only Python's standard library and requires internet access.
It replaces both source files and this note. Hashes record the downloaded
version so a later provider change can be identified. Rerun the population
cleaning script after refreshing the inputs.
