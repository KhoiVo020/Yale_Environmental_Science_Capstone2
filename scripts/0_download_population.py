"""Refresh the original Census inputs used by the population cleaning script.

Run this from the repository root with Python 3:
    python scripts/0_download_population.py

This downloads public Census files; it does not need an API key. Running it
again replaces the two source files and their provenance notes.
"""

import csv
import hashlib
import io
from datetime import date
from pathlib import Path
from urllib.request import urlopen


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "raw_data" / "population"
POPULATION_URL = (
    "https://www2.census.gov/programs-surveys/decennial/2020/data/"
    "demographic-and-housing-characteristics-file/population-pyramid-visualization/"
    "counties-populationpyramid-2000-2010-2020.csv"
)
COUNTY_CODES_URL = (
    "https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"
)
LANDING_PAGE = (
    "https://www.census.gov/library/visualizations/interactive/"
    "how-has-our-nations-population-changed.html"
)
DOCUMENTATION_URL = (
    "https://www2.census.gov/programs-surveys/decennial/2020/data/"
    "demographic-and-housing-characteristics-file/population-pyramid-visualization/"
    "population-changed-technical-documentation.pdf"
)


def download(url):
    """Read a public file into memory so the national CSV stays out of Git."""
    with urlopen(url, timeout=120) as response:
        return response.read()


def main():
    population_bytes = download(POPULATION_URL)
    county_code_bytes = download(COUNTY_CODES_URL)

    # Keep all California counties, years, and population groups here. The
    # cleaning script will select our two counties and total population rows.
    # The provider CSV uses Windows-1252, including an en dash for some missing
    # measures. Decode it explicitly so those symbols are not lost.
    reader = csv.DictReader(io.StringIO(population_bytes.decode("cp1252")))
    if not {"State", "County", "Year", "Group", "Population"}.issubset(
        reader.fieldnames or []
    ):
        raise ValueError("The Census population file has unexpected columns.")
    california_rows = [row for row in reader if row["State"] == "California"]
    if not california_rows:
        raise ValueError("No California records were found in the source file.")

    # csv handles commas inside quoted population counts. Preserve every field
    # as text, including the provider's missing-value symbols.
    subset = io.StringIO(newline="")
    writer = csv.DictWriter(subset, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(california_rows)
    subset_bytes = subset.getvalue().encode("utf-8")

    if not county_code_bytes.startswith(b"STATE|STATEFP|COUNTYFP|"):
        raise ValueError("The Census county-code file has an unexpected header.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "ca_county_population_source.csv").write_bytes(subset_bytes)
    # Save the FIPS file exactly as downloaded, including its original encoding
    # and line endings. These identifiers need to stay text when they are read.
    (OUTPUT_DIR / "national_county2020.txt").write_bytes(county_code_bytes)

    source_hash = hashlib.sha256(population_bytes).hexdigest()
    subset_hash = hashlib.sha256(subset_bytes).hexdigest()
    codes_hash = hashlib.sha256(county_code_bytes).hexdigest()
    notes = f"""# Population source notes

Retrieved: {date.today().isoformat()} (local calendar date).

## County population

Provider: U.S. Census Bureau. The county CSV accompanies *How Has Our Nation's
Population Changed?*, published May 25, 2023.

- [Dataset page]({LANDING_PAGE})
- [Original national CSV]({POPULATION_URL})
- [Technical documentation]({DOCUMENTATION_URL})

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

- Extract rows, excluding header: {len(california_rows):,}
- Extract columns: {len(reader.fieldnames)}
- National source bytes: {len(population_bytes):,}
- National source SHA-256: `{source_hash}`
- California extract SHA-256: `{subset_hash}`

The full national CSV is downloaded into memory and is not stored in this
repository. The extract contains enough rows to practice filtering counties,
years, and population groups before preparing the six study observations.

## County identifiers

`national_county2020.txt` is the unchanged [2020 Census national county-code
file]({COUNTY_CODES_URL}), separated by `|`. Read `STATEFP` and `COUNTYFP` as
text, then concatenate them to make the five-character `GEOID`.

| County | State FIPS | County FIPS | GEOID |
| --- | --- | --- | --- |
| Orange County, California | 06 | 059 | 06059 |
| Riverside County, California | 06 | 065 | 06065 |

The population CSV has county and state names but no FIPS codes. Match both
state and county name to this lookup before linking the population table to
the 2020 TIGER/Line county boundaries.

- Original county-code file bytes: {len(county_code_bytes):,}
- Original county-code file SHA-256: `{codes_hash}`

## Refresh these inputs

From the repository root, run:

```sh
python scripts/0_download_population.py
```

The script uses only Python's standard library and requires internet access.
It replaces both source files and this note. Hashes record the downloaded
version so a later provider change can be identified. Rerun the population
cleaning script after refreshing the inputs.
"""
    (OUTPUT_DIR / "source_notes.md").write_text(notes, encoding="utf-8", newline="\n")
    print(f"Saved {len(california_rows):,} California source rows to {OUTPUT_DIR}")
    print(f"Population source SHA-256: {source_hash}")
    print(f"California extract SHA-256: {subset_hash}")
    print(f"County-code source SHA-256: {codes_hash}")


if __name__ == "__main__":
    main()
