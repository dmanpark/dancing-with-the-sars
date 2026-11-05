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

## Documents

| Document | Link |
| --- | --- |
| DSWx-HLS product specification, JPL D-107395 Rev B, 10 Jul 2024 | https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/opera/OPERA_DSWx-HLS_ProductSpec_v1.0.0_D-107395_RevB.pdf |
| DSWx-S1 product specification v0.2.1 (preliminary; its class codes disagree with the files) | https://www.earthdata.nasa.gov/s3fs-public/2023-12/ProductSpec_DSWX_S1.pdf |
