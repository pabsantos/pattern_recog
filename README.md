# Flood Classification

This project uses geospatial data and QGIS API to classify and predict flood occurrences. It processes Digital Terrain Model (DTM) and Land Use/Land Cover (LULC) data, along with flood occurrence points, to create a dataset for flood prediction modeling.

## Features

- **Data Loading**: Loads DTM and LULC raster data, and flood occurrence vector data.
- **Data Processing**:
    - Ensures all raster data has the same resolution and Coordinate Reference System (CRS).
    - Converts flood occurrence points into a raster layer.
    - Converts raster data into pandas DataFrames for analysis.
- **Output**: Generates CSV files from the processed raster data, which can be used for machine learning model training.

## Usage

1. **Installation**

- This project requires QGIS to be installed. The QGIS installation path is hardcoded in `src/main.py` and may need to be adjusted based on your system.

2. **Data**
Place your DTM, LULC, and flood data in the `data` directory. The expected file paths are:
  - DTM: `data/dtm/DTM_TTI_buffer_1km_FILLED.tif`
  - LULC: `data/lulc/lulc_utm.tif` (lulc converted to sirgas 2000 utm 23S)
  - Flood Points: `data/floods/Ocorrencias_Alag_2019.shp`

3. **Execution**
Run python from QGIS installation (MacOS example):

```bash
/Applications/QGIS-LTR.app/Contents/MacOS/bin/python3 src/main.py
```