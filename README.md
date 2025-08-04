# Flood Classification

This project uses geospatial data and QGIS API to classify and predict flood occurrences. It processes Digital Terrain Model (DTM), Land Use/Land Cover (LULC) data, flood occurrence points, and hydrological features to create a dataset for flood prediction modeling.

## Features

- **Data Loading**: Loads DTM and LULC raster data, flood occurrence vector data, and hydrological features (rivers, basins, springs, outfalls).
- **Data Processing**:
    - Ensures all raster data has the same resolution (configurable, default 50m) and Coordinate Reference System (CRS).
    - Converts flood occurrence points into a raster layer.
    - Calculates distances to hydrological features:
        - Rivers and tributaries (using buffered rasterization)
    - Creates binary rasters for basin and microbasin boundaries.
    - Converts all raster data into pandas DataFrames.
    - Merges all features into a single dataset.
- **Output**: Generates a parquet file from the processed raster data, which can be used for machine learning model training.

## Data Requirements

The project expects the following data structure in the `data` directory:

### Raster Data
- **DTM**: `data/DigitalTerrainModel/DTM_TTI_buffer_1km_FILLED.tif`
- **LULC**: `data/LandUseLandCover/LULC_10m_TTI_clipped_1km.tif`

### Vector Data
- **Flood Points**: `data/SHP_floods_2019/Ocorrencias_Alag_2019.shp`
- **River Network**: `data/SHP_Tamanduatei/Rio_Tamanduatei.shp`
- **Tributaries**: `data/SHP_Tamanduatei/Afluentes_Tamanduatei.shp`
- **Main Basin**: `data/SHP_Tamanduatei/Bacia_Tamanduatei.shp`

## Output Files

The processing generates the following files in the `temp` directory:

### Final Dataset
- `final_data.parquet`: Comprehensive dataset with all features merged
  - `dtm_value`: Elevation values from DTM
  - `lulc_code`: Land use/land cover classification codes
  - `flood_binary`: Binary flood occurrence (1 = flood, 0 = no flood)
  - `dist_to_river`: Distance to nearest river (meters)
  - `dist_to_tributaries`: Distance to nearest tributary (meters)
  - `is_basin`: Binary main basin membership (1 = inside, 0 = outside)
  - `x`, `y`: Spatial coordinates

## Key Features

### Distance Calculation
- **Multi-feature layers**: Rivers and tributaries use buffered rasterization followed by proximity analysis
- **Single point features**: Springs and outfalls use direct point-to-pixel distance calculation for higher accuracy
- **Extent handling**: Automatically expands processing bounds when vector features extend beyond raster extent

### Error Handling
- Validates input data (feature counts, geometry types, spatial extents)
- Handles CRS mismatches with automatic reprojection
- Provides fallback values for missing or invalid data
- Comprehensive logging and debugging information

### Configurable Resolution
- Default processing resolution: 50 meters
- Automatically resamples all inputs to target resolution
- Maintains spatial alignment across all datasets

## Usage

1. **Data Preparation**
   Ensure all required data files are placed in the correct directory structure as specified above.

2. **Execution**

Run the project with Docker:

```bash
docker compose run --rm qgis-app
```

## Configuration

You can modify the target resolution by changing the `target_resolution` variable in `main.py`:

```python
target_resolution = 50.0  # Resolution in meters
```