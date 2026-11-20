# Prepare decennial population counts for Orange and Riverside Counties.
# Inputs: the Census CSV and county code file in raw_data/population/.
# Outputs: a six-row population table, growth summaries, and cleaning checks.
# Run from the repository folder: Rscript scripts/1_clean_population.R

library(dplyr)
library(readr)

clean_population <- function(raw_population, county_codes) {
  needed <- c("State", "County", "Year", "Group", "Population")
  if (!all(needed %in% names(raw_population))) {
    stop("The population file is missing an expected Census column.")
  }

  # Keep FIPS components as text. Otherwise California's leading zero is lost.
  county_lookup <- county_codes |>
    filter(STATE == "CA", COUNTYFP %in% c("059", "065")) |>
    transmute(county = COUNTYNAME, geoid = paste0(STATEFP, COUNTYFP))
  if (nrow(county_lookup) != 2 || anyDuplicated(county_lookup$county)) {
    stop("Expected one county code for Orange and one for Riverside.")
  }

  # The source includes demographic subgroups as well as county totals.
  # Selecting Total Population avoids adding overlapping groups together.
  selected <- raw_population |>
    filter(
      State == "California",
      County %in% c("Orange County", "Riverside County"),
      Year %in% c("2000", "2010", "2020"),
      Group == "Total Population"
    ) |>
    select(county = County, year = Year, population = Population)

  # Remove only exact repeated observations. Different counts for the same
  # county and year should be investigated, not averaged or silently dropped.
  duplicate_rows <- nrow(selected) - nrow(distinct(selected))
  selected <- distinct(selected)
  if (anyDuplicated(selected[c("county", "year")])) {
    stop("Conflicting population counts exist for a county-year.")
  }

  # Census prints thousands separators, so parse counts before calculations.
  # Require numeric count text rather than letting labels turn into numbers.
  if (any(is.na(selected$population)) ||
      any(!grepl("^[0-9]+$", gsub(",", "", selected$population, fixed = TRUE)))) {
    stop("A selected population count is missing or is not numeric.")
  }
  population <- selected |>
    mutate(year = as.integer(year), population = parse_number(population)) |>
    left_join(county_lookup, by = "county", relationship = "many-to-one") |>
    select(geoid, county, year, population) |>
    arrange(geoid, year)

  if (nrow(population) != 6 || anyNA(population) ||
      any(population$population <= 0) ||
      any(population$population %% 1 != 0) ||
      !setequal(population$geoid, c("06059", "06065"))) {
    stop("Expected six complete, positive county-year population counts.")
  }
  coverage <- population |> count(geoid, name = "years_present")
  if (any(coverage$years_present != 3)) {
    stop("Each county must have all three census years.")
  }

  list(data = population, duplicates_removed = duplicate_rows)
}


# The supplied snapshots make this step reproducible without an API key.
raw_population <- read_csv(
  "raw_data/population/ca_county_population_source.csv",
  col_types = cols(.default = col_character())
)
county_codes <- read_delim(
  "raw_data/population/national_county2020.txt",
  delim = "|", col_types = cols(.default = col_character())
)
cleaned <- clean_population(raw_population, county_codes)
population <- cleaned$data

# Calculate changes within each county, so Orange is never compared with
# Riverside's previous observation. These are ten-year, not annual, changes.
growth <- population |>
  group_by(geoid, county) |>
  arrange(year, .by_group = TRUE) |>
  mutate(
    start_year = lag(year),
    starting_population = lag(population),
    population_change = population - starting_population,
    population_change_pct = 100 * population_change / starting_population
  ) |>
  filter(!is.na(start_year)) |>
  ungroup() |>
  select(geoid, county, start_year, end_year = year,
         starting_population, ending_population = population,
         population_change, population_change_pct)

# Summarise the full study period separately from the two decade changes.
study_summary <- population |>
  group_by(geoid, county) |>
  summarise(
    census_years = n_distinct(year),
    population_2000 = population[year == 2000],
    population_2020 = population[year == 2020],
    .groups = "drop"
  ) |>
  mutate(
    population_change = population_2020 - population_2000,
    population_change_pct = 100 * population_change / population_2000
  )

dir.create("clean_data", showWarnings = FALSE)
dir.create("results", showWarnings = FALSE)
write_csv(population, "clean_data/county_population.csv")
write_csv(growth, "results/population_change_by_decade.csv")
write_csv(study_summary, "results/population_change_2000_2020.csv")

report <- c(
  "Decennial Census population preprocessing",
  paste("Rows in California source snapshot:", nrow(raw_population)),
  paste("Exact duplicate selected observations removed:", cleaned$duplicates_removed),
  paste("Clean county-year observations:", nrow(population)),
  "Counties: Orange (06059), Riverside (06065)",
  "Years per county: 2000, 2010, 2020",
  "Missing population counts: 0",
  "Missing county identifiers: 0",
  "Conflicting county-year observations: 0",
  "Population counts were not estimated or imputed.",
  "Land-cover areas and conversions have not yet been calculated."
)
writeLines(report, "results/population_cleaning_report.txt")
cat(paste(report, collapse = "\n"), "\n")
