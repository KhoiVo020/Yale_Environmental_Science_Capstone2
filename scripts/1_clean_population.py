"""Prepare Census population counts for Orange and Riverside Counties.

Inputs: the Census CSV and county code file in raw_data/population/.
Outputs: a six-row population table, growth summaries, and cleaning checks.
Run with: python scripts/1_clean_population.py
"""

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
YEARS = [2000, 2010, 2020]
COUNTIES = {"Orange County": "06059", "Riverside County": "06065"}


def clean_population(raw_population, county_codes):
    """Return the six study observations and the number of exact duplicates removed."""
    needed = {"State", "County", "Year", "Group", "Population"}
    if not needed.issubset(raw_population.columns):
        raise ValueError("The population file is missing an expected Census column.")
    if not {"STATE", "STATEFP", "COUNTYFP", "COUNTYNAME"}.issubset(county_codes.columns):
        raise ValueError("The county-code file is missing an expected column.")

    # FIPS components are read as text so California's leading zero survives.
    lookup = county_codes.loc[
        county_codes["STATE"].eq("CA") & county_codes["COUNTYFP"].isin(["059", "065"])
    ].copy()
    lookup["geoid"] = lookup["STATEFP"] + lookup["COUNTYFP"]
    lookup = lookup.rename(columns={"COUNTYNAME": "county"})[["county", "geoid"]]
    if len(lookup) != 2 or dict(zip(lookup["county"], lookup["geoid"])) != COUNTIES:
        raise ValueError("Expected the official codes for Orange and Riverside Counties.")

    # The demographic groups overlap. Use Total Population instead of adding
    # those groups together and counting the same residents more than once.
    selected = raw_population.loc[
        raw_population["State"].eq("California")
        & raw_population["County"].isin(COUNTIES)
        & raw_population["Year"].isin([str(year) for year in YEARS])
        & raw_population["Group"].eq("Total Population"),
        ["County", "Year", "Population"],
    ].rename(columns={"County": "county", "Year": "year", "Population": "population"})

    # Exact repeated observations add nothing. Conflicting counts for a
    # county-year need investigation, so stop instead of choosing a value.
    duplicates_removed = len(selected) - len(selected.drop_duplicates())
    selected = selected.drop_duplicates().copy()
    if selected.duplicated(["county", "year"]).any():
        raise ValueError("Conflicting population counts exist for a county-year.")

    # The source prints commas in counts. Remove them before converting to
    # integers, and reject missing values or labels instead of guessing.
    count_text = selected["population"].str.replace(",", "", regex=False)
    if not count_text.str.fullmatch(r"[0-9]+", na=False).all():
        raise ValueError("A selected population count is missing or is not numeric.")
    selected["population"] = pd.to_numeric(count_text, errors="raise").astype("int64")
    selected["year"] = selected["year"].astype(int)
    population = selected.merge(lookup, on="county", how="left", validate="many_to_one")
    population = population[["geoid", "county", "year", "population"]]
    population = population.sort_values(["geoid", "year"]).reset_index(drop=True)

    expected = {(geoid, year) for geoid in COUNTIES.values() for year in YEARS}
    observed = set(zip(population["geoid"], population["year"]))
    if observed != expected or population.isna().any().any():
        raise ValueError("Expected all six county-year observations with no missing fields.")
    if (population["population"] <= 0).any():
        raise ValueError("Population counts must be positive.")

    return population, duplicates_removed


def main():
    # Resolve paths from this file, so no personal working-directory path is
    # needed. The saved inputs also avoid requiring a Census API key.
    source_dir = PROJECT_DIR / "raw_data" / "population"
    raw_population = pd.read_csv(source_dir / "ca_county_population_source.csv", dtype=str)
    county_codes = pd.read_csv(source_dir / "national_county2020.txt", sep="|", dtype=str)
    population, duplicates_removed = clean_population(raw_population, county_codes)

    # Shift within each county so Orange is never compared with Riverside's
    # previous observation. Each comparison covers ten years, not one year.
    growth = population.copy()
    previous = growth.groupby("geoid")[["year", "population"]].shift(1)
    growth["start_year"] = previous["year"]
    growth["starting_population"] = previous["population"]
    growth = growth.dropna(subset=["start_year"]).copy()
    growth[["start_year", "starting_population"]] = growth[
        ["start_year", "starting_population"]
    ].astype("int64")
    growth = growth.rename(columns={"year": "end_year", "population": "ending_population"})
    growth["population_change"] = growth["ending_population"] - growth["starting_population"]
    growth["population_change_pct"] = (
        100 * growth["population_change"] / growth["starting_population"]
    )
    growth = growth[
        ["geoid", "county", "start_year", "end_year", "starting_population",
         "ending_population", "population_change", "population_change_pct"]
    ]

    # The validated table is sorted by year, so first and last are 2000 and
    # 2020. Summarize the full period separately from the two decade changes.
    study_summary = population.groupby(["geoid", "county"], as_index=False).agg(
        census_years=("year", "nunique"),
        population_2000=("population", "first"),
        population_2020=("population", "last"),
    )
    study_summary["population_change"] = (
        study_summary["population_2020"] - study_summary["population_2000"]
    )
    study_summary["population_change_pct"] = (
        100 * study_summary["population_change"] / study_summary["population_2000"]
    )

    clean_dir = PROJECT_DIR / "clean_data"
    results_dir = PROJECT_DIR / "results"
    clean_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)
    population.to_csv(clean_dir / "county_population.csv", index=False, lineterminator="\n")
    growth.to_csv(results_dir / "population_change_by_decade.csv", index=False, lineterminator="\n")
    study_summary.to_csv(
        results_dir / "population_change_2000_2020.csv", index=False, lineterminator="\n"
    )

    report = [
        "Decennial Census population preprocessing",
        f"Rows in California source snapshot: {len(raw_population)}",
        f"Exact duplicate selected observations removed: {duplicates_removed}",
        f"Clean county-year observations: {len(population)}",
        "Counties: Orange (06059), Riverside (06065)",
        "Years per county: 2000, 2010, 2020",
        "Missing population counts: 0",
        "Missing county identifiers: 0",
        "Conflicting county-year observations: 0",
        "Population counts were not estimated or imputed.",
        "Land-cover areas and conversions have not yet been calculated.",
    ]
    report_text = "\n".join(report) + "\n"
    (results_dir / "population_cleaning_report.txt").write_text(
        report_text, encoding="utf-8", newline="\n"
    )
    print(report_text, end="")


if __name__ == "__main__":
    main()
