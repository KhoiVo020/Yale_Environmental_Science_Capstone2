# Clean data dictionary

The cleaned table has one row per month for January 1975 through December 2025: 612 rows. CO2 concentrations are dry-air mole fractions in parts per million (ppm).

| Clean column | Raw column | Meaning |
| --- | --- | --- |
| `date` | Derived | First-of-month label in `YYYY-MM-DD` format; an index, not a sampling date. |
| `year` | `year` | Calendar year. |
| `month` | `month` | Calendar month, 1–12. |
| `decimal_date` | `decimal date` | NOAA's decimal-year time coordinate, retained as supplied. |
| `co2_ppm` | `average` | Monthly mean CO2, centered on midmonth by NOAA. |
| `deseasonalized_co2_ppm` | `deseasonalized` | Monthly CO2 after NOAA's seasonal adjustment. |
| `days_measured` | `ndays` | Number of contributing daily means. |
| `daily_sd_ppm` | `sdev` | Standard deviation of daily means (ppm). |
| `monthly_uncertainty_ppm` | `unc` | NOAA's uncertainty of the monthly mean (ppm). |
| `quality_info_missing` | Derived | Boolean: any negative or blank `ndays`, `sdev`, or `unc` before cleaning. |

Negative markers in the five measurement/count columns become blank missing values. The script adds no imputed values, removes no outliers, and does not repeat NOAA's seasonal adjustment. Definitions follow the [NOAA text-file header](https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.txt) and [measurement description](https://gml.noaa.gov/ccgg/trends/).

The quality flag identifies December 1975 and April 1984 in this analysis period. It signals unavailable quality information, not a definitive interpolation classification. Their supplied uncertainty values of zero are retained as zero; neither zero nor the flag establishes error-free measurement. NOAA has already interpolated some values in the source record.
