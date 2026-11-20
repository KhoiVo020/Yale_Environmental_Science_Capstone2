# Atmospheric CO2 in the Mauna Loa record, 1975-2025

Capstone project for the Yale Environmental Data Science Certificate.

## Project description

Atmospheric carbon dioxide changes over both years and seasons. This project uses NOAA's monthly Mauna Loa record to examine the long-term change in CO2 while keeping the seasonal cycle visible. The current stage prepares the data and checks its completeness; plots and trend comparisons will follow.

## Research question

**How did atmospheric CO2 in the Mauna Loa record change from 1975 to 2025, and how does the recurring seasonal cycle differ from the long-term trend?**

The analysis will use the monthly mean and NOAA's existing deseasonalized series. It will describe changes in this record, rather than try to attribute them to individual emission sources.

## Dataset

The project uses the **Mauna Loa monthly mean CO2 dataset** from [NOAA's Global Monitoring Laboratory](https://gml.noaa.gov/ccgg/trends/data.html). Concentrations are dry-air mole fractions in parts per million (ppm). The original download contains 824 monthly records, from March 1958 through October 2026, along with day counts and variability/uncertainty fields.

The included [CSV snapshot](raw_data/co2_mm_mlo.csv) was downloaded on November 19, 2026. Its provider comments are preserved. [Source notes](raw_data/README.md) record the download link, attribution, and file checksum; the [data dictionary](docs/data_dictionary.md) explains the cleaned columns.

The study period is January 1975 through December 2025. NOAA began its measurements in May 1974, so 1975 is the first full NOAA calendar year. Ending in 2025 avoids comparing an incomplete 2026 with complete years. Earlier records remain in the original file but are outside this project's current scope. The course's synthetic stream-temperature examples are not used as research data.

## Repository contents

```text
Yale_Environmental_Science_Capstone2/
|-- README.md
|-- requirements.txt
|-- raw_data/
|   |-- README.md                  # Source and download details
|   `-- co2_mm_mlo.csv             # Original NOAA file; never overwritten
|-- clean_data/
|   `-- co2_monthly_clean.csv      # One row per month, 1975-2025
|-- scripts/
|   `-- 1_clean_co2.py             # Commented preprocessing script
|-- results/
|   |-- cleaning_report.txt        # Counts and quality checks
|   `-- yearly_coverage.csv        # Available months in each year
|-- figures/                      # Reserved for later plots
`-- docs/
    |-- data_dictionary.md
    `-- capstone_prompt_2_response.md
```

## Run the preprocessing

The script uses Python and pandas. It was tested with Python 3.13.1 and pandas 2.2.3. From the repository folder, run:

```bash
python -m pip install -r requirements.txt
python scripts/1_clean_co2.py
```

The raw data are included, so preprocessing needs no network connection after pandas is installed. Running the script again replaces only the generated CSVs and cleaning report. Paths are based on the script's location, so there is no personal directory to edit.

## Cleaning decisions and checks

- Rename the source columns to make their meanings and units clear, and check that their contents are numeric.
- Check for duplicate months. Remove exact repeated rows, but stop if two records give different values for the same month. No duplicates were found in this snapshot.
- Select 1975-2025, construct a monthly date index, and sort chronologically. The date uses day 1 for indexing; it is not a daily observation.
- Convert negative missing-information markers to blanks. Record missing quality information in `quality_info_missing` before replacing the markers. Keep published zero uncertainty values as zero.
- Retain both CO2 series and all months in the study period. No new interpolation, outlier removal, or seasonal adjustment is applied.
- Check for missing calendar months and save yearly coverage counts before calculating any annual statistics.

The [cleaning report](results/cleaning_report.txt) records **612 months across 51 complete years**, with no missing CO2 means. December 1975 and April 1984 have missing quality metadata. Their CO2 means are retained and flagged so they can be checked in later analysis.

## Limitations and next steps

NOAA has already processed these monthly means and interpolated some missing months. The quality flag records missing metadata; it is not a complete classification of interpolated values. A published zero uncertainty should not be interpreted as perfect certainty.

The record also includes temporary measurements at Maunakea from December 2022 through July 4, 2023. This is a background atmospheric record, not a global surface mean. NOAA may revise published values, so the saved snapshot makes this stage reproducible. These details are described in [NOAA's documentation](https://gml.noaa.gov/ccgg/trends/).

Next, plot both series, summarize complete calendar years, and examine the monthly seasonal pattern. Compare the trend with and without the two flagged months and discuss the temporary monitoring-site change before drawing conclusions. The files in `results/` currently report preprocessing checks, not final research findings.

## Assistance

OpenAI Codex assisted with selecting this working topic, drafting the code and documentation, and running validation checks.
