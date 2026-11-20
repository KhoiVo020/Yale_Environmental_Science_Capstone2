"""Prepare NOAA's monthly Mauna Loa CO2 record for the capstone.

Input: raw_data/co2_mm_mlo.csv (the original NOAA download).
Outputs: clean_data/co2_monthly_clean.csv and two checks in results/.
Run with: python scripts/1_clean_co2.py
"""

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
START_YEAR = 1975
END_YEAR = 2025

COLUMN_NAMES = {
    "year": "year",
    "month": "month",
    "decimal date": "decimal_date",
    "average": "co2_ppm",
    "deseasonalized": "deseasonalized_co2_ppm",
    "ndays": "days_measured",
    "sdev": "daily_sd_ppm",
    "unc": "monthly_uncertainty_ppm",
}


def clean_monthly_data(raw):
    """Return one row per month for 1975-2025, plus a duplicate count."""
    missing_columns = set(COLUMN_NAMES) - set(raw.columns)
    if missing_columns:
        raise ValueError(f"Missing source columns: {sorted(missing_columns)}")

    # An exact repeated row adds no information. Different values for the
    # same month need review, so the script stops rather than choosing one.
    data = raw.drop_duplicates().copy()
    duplicates_removed = len(raw) - len(data)
    data = data[list(COLUMN_NAMES)].rename(columns=COLUMN_NAMES)
    for column in data.columns:
        data[column] = pd.to_numeric(data[column], errors="raise")

    for column in ["year", "month"]:
        if data[column].isna().any() or (data[column] % 1 != 0).any():
            raise ValueError(f"{column} must contain whole numbers with no blanks.")
        data[column] = data[column].astype(int)
    if not data["month"].between(1, 12).all():
        raise ValueError("Month values must be between 1 and 12.")
    if data.duplicated(["year", "month"]).any():
        raise ValueError("Conflicting records for the same month need review.")

    # Start with the first complete calendar year after NOAA began measuring
    # in May 1974. Stop at 2025 so the incomplete 2026 year is not compared
    # with full years. Keep the entire original download in raw_data/.
    data = data.loc[data["year"].between(START_YEAR, END_YEAR)].copy()
    if data.empty:
        raise ValueError("The input contains no months in the study period.")

    # These negative numbers are missing-information markers, not real
    # counts or uncertainties. Save their presence before replacing them.
    # This flag alone cannot identify every interpolated source value.
    quality_columns = ["days_measured", "daily_sd_ppm", "monthly_uncertainty_ppm"]
    data["quality_info_missing"] = (
        data[quality_columns].lt(0) | data[quality_columns].isna()
    ).any(axis=1)
    value_columns = ["co2_ppm", "deseasonalized_co2_ppm"] + quality_columns
    for column in value_columns:
        data[column] = data[column].mask(data[column] < 0)
    # Zero uncertainty is retained as published; it is not a negative marker.
    data["days_measured"] = data["days_measured"].astype("Int64")

    # Day 1 is only a convenient monthly index. NOAA's published means are
    # centered on the middle of the month, not measured on this single day.
    dates = pd.to_datetime(data[["year", "month"]].assign(day=1))
    data.insert(0, "date", dates)
    data = data.sort_values("date").reset_index(drop=True)

    # A missing row is different from a row with a missing measurement.
    # Stop on missing calendar months instead of silently closing the gap.
    expected_dates = pd.date_range(
        f"{START_YEAR}-01-01", f"{END_YEAR}-12-01", freq="MS"
    )
    missing_dates = expected_dates.difference(data["date"])
    if len(missing_dates):
        raise ValueError(f"Missing calendar months: {missing_dates.strftime('%Y-%m').tolist()}")

    # Keep both NOAA series: the monthly mean retains the seasonal cycle,
    # while NOAA's deseasonalized series helps examine the longer-term trend.
    # Do not fill missing concentrations or remove high observations here.
    return data, duplicates_removed


def main():
    # Resolve paths from this script so it also runs outside the repo folder.
    raw_path = PROJECT_DIR / "raw_data" / "co2_mm_mlo.csv"
    raw = pd.read_csv(raw_path, comment="#")
    clean, duplicates_removed = clean_monthly_data(raw)

    clean_dir = PROJECT_DIR / "clean_data"
    results_dir = PROJECT_DIR / "results"
    clean_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)

    clean.to_csv(
        clean_dir / "co2_monthly_clean.csv",
        index=False,
        date_format="%Y-%m-%d",
        lineterminator="\n",
    )

    # Counts make incomplete years and missing quality information visible
    # before any annual averages or trend estimates are calculated.
    coverage = clean.groupby("year", as_index=False).agg(
        months_present=("month", "size"),
        months_with_co2=("co2_ppm", "count"),
        months_with_deseasonalized_co2=("deseasonalized_co2_ppm", "count"),
        months_missing_quality_info=("quality_info_missing", "sum"),
    )
    coverage.to_csv(results_dir / "yearly_coverage.csv", index=False, lineterminator="\n")

    flagged_months = clean.loc[clean["quality_info_missing"], "date"]
    report = [
        "NOAA monthly CO2 preprocessing checks",
        f"Source rows: {len(raw)}",
        f"Exact duplicate rows removed: {duplicates_removed}",
        f"Rows outside {START_YEAR}-{END_YEAR}: {len(raw) - duplicates_removed - len(clean)}",
        f"Clean rows: {len(clean)}",
        f"First month: {clean['date'].min():%Y-%m}",
        f"Last month: {clean['date'].max():%Y-%m}",
        "Duplicate year-months after cleaning: 0",
        "Missing calendar months in study period: 0",
        f"Missing monthly CO2 values: {clean['co2_ppm'].isna().sum()}",
        f"Missing deseasonalized CO2 values: {clean['deseasonalized_co2_ppm'].isna().sum()}",
        f"Months with missing quality information: {len(flagged_months)}",
        "Flagged months: " + (", ".join(flagged_months.dt.strftime("%Y-%m")) or "none"),
        "Missing values were not filled; published CO2 means were retained.",
    ]
    report_text = "\n".join(report) + "\n"
    (results_dir / "cleaning_report.txt").write_text(
        report_text, encoding="utf-8", newline="\n"
    )
    print(report_text, end="")


if __name__ == "__main__":
    main()
