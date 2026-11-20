"""Download 2020 TIGER county boundaries and keep the two study counties.

Optional refresh: python scripts/0_prepare_boundaries.py
Requires the packages in requirements.txt. The small GeoJSON is already
included; the full national ZIP is cached locally and excluded from Git.
"""

import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.request import urlopen

import geopandas as gpd


PROJECT_DIR = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://www2.census.gov/geo/tiger/TIGER2020/COUNTY/tl_2020_us_county.zip"


def main():
    folder = PROJECT_DIR / "raw_data" / "boundaries"
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / "tl_2020_us_county.zip"

    # Cache the 77 MB national file so a repeated run does not download it again.
    if not archive.exists():
        with urlopen(SOURCE_URL, timeout=60) as response:
            archive.write_bytes(response.read())

    counties = gpd.read_file(
        archive, where="STATEFP = '06' AND COUNTYFP IN ('059', '065')"
    ).sort_values("GEOID")
    if len(counties) != 2 or set(counties.GEOID) != {"06059", "06065"}:
        raise ValueError("Expected only Orange and Riverside Counties.")
    if counties.geometry.is_empty.any() or not counties.geometry.is_valid.all():
        raise ValueError("A county boundary is empty or invalid; inspect the source.")

    # GeoJSON uses longitude/latitude. Transform the original NAD83 coordinates
    # to WGS84, retaining all attributes and the unsimplified boundaries.
    # Later area calculations must use the land-cover raster's equal-area CRS.
    output = folder / "study_counties_2020.geojson"
    counties.to_crs("EPSG:4326").to_file(output, driver="GeoJSON")

    metadata = {
        "source_url": SOURCE_URL,
        "prepared": date.today().isoformat(),
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "subset_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "selection": "STATEFP = '06' AND COUNTYFP IN ('059', '065')",
        "processing": "Selected two features; retained attributes; transformed NAD83 to WGS84; no simplification.",
        "note": "The full ZIP is a local cache excluded from Git; prepared is the subset creation date.",
    }
    (folder / "source_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Saved {len(counties)} counties to {output}")


if __name__ == "__main__":
    main()
