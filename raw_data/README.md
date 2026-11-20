# Raw data

`co2_mm_mlo.csv` is an unchanged snapshot of NOAA Global Monitoring Laboratory's [Mauna Loa monthly CO2 dataset](https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv), downloaded November 19, 2026. It contains 824 monthly records from March 1958 through October 2026, plus the original provider notes. The cleaning script reads this file without overwriting it.

SHA-256: `163cadae3baa6dec7d3ae066108b50d1018a78447b1b6fc2b6e3936465549d16`

Data credit: Xin Lan, NOAA/GML, and Ralph Keeling, Scripps Institution of Oceanography, following the [NOAA data page](https://gml.noaa.gov/ccgg/trends/data.html). That page also notes that quality checks can lead to revisions. Keeping this snapshot makes the analysis reproducible.

This is an atmospheric monitoring record, not a global average. After the volcanic eruption, observations from December 2022 through July 4, 2023 came from Maunakea; July 2023 spans the return to Mauna Loa and has mixed site provenance. See [NOAA's record description](https://gml.noaa.gov/ccgg/trends/) for the measurement context.
