# Citations

Data, software and documents this project uses, with where each was fetched. Started in pre-event prep on 5 Nov 2026 (`prompts/build.md` Phase 0 step 5); completed during the event. Licences and formal citations are added in Phase 6, after checking each publisher's own terms.

## Radar and reference products (NASA Earthdata)

| Product | Used for | Fetched from |
| --- | --- | --- |
| NISAR L2 GCOV, provisional (`NISAR_L2_GCOV_PROVISIONAL_V1`), frequency A, HH and HV | Every NISAR layer, both events | ASF, https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_PROVISIONAL_V1/ ; granules listed in `data/manifest.csv` |
| OPERA L3 DSWx-HLS v1 (`OPERA_L3_DSWX-HLS_V1`), `B01_WTR` | Optical referee | PO.DAAC, https://search.earthdata.nasa.gov/search/granules?p=C2617126679-POCLOUD |
| OPERA L3 DSWx-S1 v1 (`OPERA_L3_DSWX-S1_V1`), `B01_WTR` | Sentinel-1's own water map; claim 1 comparison | PO.DAAC, https://search.earthdata.nasa.gov/search/granules?p=C2949811996-POCLOUD |
| OPERA L2 RTC-S1 v1 (`OPERA_L2_RTC-S1_V1`), VV, VH, mask and `.h5` per burst | Sentinel-1 flood maps and our DSWx-S1 runs | ASF, https://search.earthdata.nasa.gov/search/granules?p=C2777436413-ASF |

## Ancillary layers

Download locations as recorded by the preliminary tests (checked 4 Nov 2026) and used again on 5 Nov 2026 for the north Bihar frame. Tiles on disk cover both NISAR frames: Gandak (track 149, frame 75, lon 81.87 to 85.38°E, lat 25.18 to 28.28°N) and north Bihar (track 48, frame 75, lon 83.89 to 87.44°E, lat 25.17 to 28.29°N).

| Layer | Tiles | Fetched from |
| --- | --- | --- |
| Copernicus GLO-30 DEM | N25 to N28, E081 to E087 (28) | `https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N{lat}_00_E{lon}_00_DEM/Copernicus_DSM_COG_10_N{lat}_00_E{lon}_00_DEM.tif`; AWS Registry of Open Data, https://registry.opendata.aws/copernicus-dem/ |
| GLO-30 HAND (2021, v1) | N25 to N28, E081 to E087 (28) | `https://glo-30-hand.s3.amazonaws.com/v1/2021/Copernicus_DSM_COG_10_N{lat}_00_E{lon}_00_HAND.tif`; https://registry.opendata.aws/glo-30-hand/ |
| ESA WorldCover 2021 v200, 10 m | N24 and N27, E081, E084 and E087 (6) | `https://esa-worldcover.s3.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tile}_Map.tif`; https://registry.opendata.aws/esa-worldcover-vito/ |
| JRC Global Surface Water occurrence v1.4 (1984 to 2021) | 80E_30N (1) | https://storage.googleapis.com/global-surface-water/downloads2021/occurrence/occurrence_80E_30Nv1_4_2021.tif ; https://global-surface-water.appspot.com/download |
| GHSL GHS-BUILT-S E2020 R2023A, 100 m, Mollweide | R6_C26 and R6_C27 (2) | `https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_S_GLOBE_R2023A/GHS_BUILT_S_E2020_GLOBE_R2023A_54009_100/V1-0/tiles/GHS_BUILT_S_E2020_GLOBE_R2023A_54009_100_V1_0_R6_C{26,27}.zip`; JRC GHSL data portal |

## Software

| Software | Version | Source |
| --- | --- | --- |
| DSWX-SAR (OPERA) | tag DSWx-NI-v1.0 | https://github.com/opera-adt/DSWX-SAR |
| MapLibre GL JS | 6.18.0 (npm, 14 Nov 2026) | https://github.com/maplibre/maplibre-gl-js ; loaded from https://cdn.jsdelivr.net/npm/maplibre-gl@6.18.0/ |
| PMTiles (JavaScript library and the `pmtiles` command-line tool) | 4.5.0 (npm); CLI 1.31.2 | https://github.com/protomaps/PMTiles |
| MapLibre GL Compare | 0.5.0 (npm) | https://github.com/maplibre/maplibre-gl-compare |
| OpenFreeMap basemap (positron style; OpenMapTiles schema, OpenStreetMap data) | live service | https://openfreemap.org/ ; https://www.openstreetmap.org/copyright |
| GDAL | 3.10.3 | https://gdal.org/ ; MBTiles driver https://gdal.org/en/stable/drivers/raster/mbtiles.html |
| Python scientific stack: numpy 2.4.6, scipy 1.17.1, h5py 3.16.0, rasterio 1.4.4, scikit-learn 1.9.1, matplotlib 3.11.2, pyproj 3.7.2 | as listed | https://numpy.org/ , https://scipy.org/ , https://www.h5py.org/ , https://rasterio.readthedocs.io/ , https://scikit-learn.org/ , https://matplotlib.org/ , https://pyproj4.github.io/pyproj/ |
| Playwright for Python | 1.64.1 | https://playwright.dev/python/ |
| FFmpeg | 9.0.2 | https://ffmpeg.org/ |
| OpenStreetMap Nominatim (breach village lookup, 14 Nov 2026) | live service | https://nominatim.openstreetmap.org/ ; Areraj village node https://www.openstreetmap.org/node/245750259 |

## News reports and context (from docs/overview.md)

| Source | Link |
| --- | --- |
| Rains swamp the Gandak River, NASA Earth Observatory | https://science.nasa.gov/earth/earth-observatory/rains-swamp-the-gandak-river/ |
| Bihar flood crisis deepens as Gandak hits record level, Daijiworld, 1 Oct 2026 | https://daijiworld.com/news/newsDisplay?newsID=1328211 |
| Flood crisis deepens as embankments breached by Gandak, Telangana Today (IANS), 1 Oct 2026 | https://telanganatoday.com/flood-crisis-deepens-in-bihar-as-embankments-breached-by-gandak-river-across-multiple-districts |
| Bihar floods: 44 lakh affected across 14 districts, Telangana Today, 10 Sep 2026 | https://telanganatoday.com/bihar-floods-44-lakh-affected-across-14-districts |
| Deriving exclusion maps from C-band SAR time series, Zhao et al., ISPRS Annals 2020 | https://isprs-annals.copernicus.org/articles/V-1-2020/395/2020/ |
| NISAR data availability and provisional known issues, ASF | https://nisar-docs.asf.alaska.edu/availability-overview/ ; https://nisar-docs.asf.alaska.edu/provisional-known-issues/ |
| NISAR L-band data released, NASA Earthdata, 21 Jul 2026 | https://www.earthdata.nasa.gov/news/nisar-l-band-data-released-expanding-record-surface-changes |
| OPERA DSWx product suite, NASA JPL | https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/ |
| OPERA DSWx-S1 and DSWx-NI ATBD | https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/opera/atbd/D-108763_Rev_A_OPERA_DSWx_S1_NI_ATBD_20240530_SIGNED.pdf |
| GitHub Pages limits | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits |

## NASA Space Apps Challenge pages (used to plan the project)

| Source | Link |
| --- | --- |
| NASA Space Apps Challenge, Participant FAQ (2022, legacy site) | https://legacy.spaceappschallenge.org/resources/faq/ |
| NASA Space Apps Challenge, Judging & Awards Guide (2024 edition) | https://www.spaceappschallenge.org/resources/judging-awards-guide |
| NASA Space Apps Challenge, Project Submission Guide | https://www.spaceappschallenge.org/resources/project-submission-guide/ |
| NASA Space Apps Challenge 2026 | https://www.spaceappschallenge.org/2026/ |
| NASA Space Apps 2025 Global Finalists | https://www.spaceappschallenge.org/2025/awards/global-finalists/ |
| NASA announces 2025 Space Apps global winners, NASA | https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-announces-2025-international-space-apps-challenge-global-winners/ |

## Documents

| Document | Link |
| --- | --- |
| DSWx-HLS product specification, JPL D-107395 Rev B, 10 Jul 2024 | https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/opera/OPERA_DSWx-HLS_ProductSpec_v1.0.0_D-107395_RevB.pdf |
| DSWx-S1 product specification v0.2.1 (preliminary; its class codes disagree with the files) | https://www.earthdata.nasa.gov/s3fs-public/2023-12/ProductSpec_DSWX_S1.pdf |

## Link check

Every link in this file and in `docs/overview.md` was requested by script on 14 Nov 2026 at 19:20 (America/Los_Angeles): 46 of 51 returned HTTP 200. The other five were fetched manually from another network on 14 and 15 Nov 2026 and load: the JPL OPERA DSWx product page (HTTP 403 to scripts) and four spaceappschallenge.org pages (the 2026 page, the 2025 Global Finalists, the Judging & Awards Guide and the Project Submission Guide), whose certificate chain did not verify from the build machine.
