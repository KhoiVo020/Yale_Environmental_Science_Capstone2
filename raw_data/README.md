# Project data

Source snapshots were obtained on November 19, 2026. Cleaning scripts read them without changing their values.

- [population/](population/source_notes.md): California rows from the Census county population file, plus the unchanged 2020 national county-code lookup. The extract preserves all 24 population groups so the Python script can select the two counties' total counts.
- [boundaries/](boundaries/README.md): the selected Orange and Riverside features from the full 2020 TIGER/Line county shapefile. This is an unsimplified subset converted to GeoJSON, not the untouched national archive.
- [land_cover/](land_cover/README.md): download instructions for Annual NLCD Collection 1.2 land-cover layers for 2000, 2010, and 2020. These rasters are not included yet.

Population provenance is recorded in `population/source_notes.md`; boundary provenance is in `boundaries/source_metadata.json`. Refresh helpers are optional. Re-run cleaning and review the changes if a source is refreshed.
