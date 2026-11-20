# Data dictionary

## Population outputs

`clean_data/county_population.csv` has one row per county and census year.

| Column | Type and meaning |
| --- | --- |
| `geoid` | Text county identifier; `06059` Orange or `06065` Riverside. Keep leading zeros. |
| `county` | County name; categorical. |
| `year` | Integer census year: 2000, 2010, or 2020. |
| `population` | Integer total residents counted in that census. |

`results/population_change_by_decade.csv` contains `geoid`, `county`,
`start_year`, `end_year`, `starting_population`, `ending_population`,
`population_change` (ending minus starting), and `population_change_pct`
(`100 * population_change / starting_population`).

`results/population_change_2000_2020.csv` contains `geoid`, `county`,
`census_years` (number of distinct observations), `population_2000`,
`population_2020`, `population_change`, and `population_change_pct` using
2000 as the baseline. See [population source notes](../raw_data/population/source_notes.md).

## Planned land-cover outputs

These tables have **not been calculated**. Land-cover codes are categories,
not numeric quantities to average.

| Conversion-table column | Meaning |
| --- | --- |
| `geoid`, `county`, `start_year`, `end_year` | County and comparison period. |
| `starting_code`, `starting_land_cover` | Original nondeveloped code and label. |
| `starting_acres` | Original class area within the common valid coverage. |
| `converted_acres` | Area of that class ending in developed codes 21-24. |
| `percent_starting_class_converted` | `100 * converted_acres / starting_acres`; `NA` if starting area is zero. |

A county-year table will join `developed_acres` to `population` by `geoid`
and `year`; `developed_acres_per_resident = developed_acres / population`.
Optional `developed_m2_per_resident` multiplies acres by 4046.8564224 before
division. Missing coverage is excluded and reported, never recorded as zero.
