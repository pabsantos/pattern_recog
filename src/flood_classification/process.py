import numpy as np
import pandas as pd
from osgeo import gdal, gdalconst
from qgis.core import QgsRasterLayer

from flood_classification import load_raster

gdal.UseExceptions()

def check_resolution_and_crs(
    raster1, raster2, path_raster1, path_raster2, resampled_path1, resampled_path2, target_resolution
):
    """
    Checks if two raster datasets have matching coordinate reference systems (CRS) and spatial resolutions.
    If the CRS do not match, raises a ValueError. If the resolutions differ, resamples the raster with higher resolution
    to match the lower resolution raster using GDAL's Warp function, and reloads the resampled raster.

    Args:
        raster1: The first raster object, expected to have methods for CRS, resolution, and extent.
        raster2: The second raster object, expected to have methods for CRS, resolution, and extent.
        path_raster1 (str): File path to the first raster.
        path_raster2 (str): File path to the second raster.
        resampled_path1 (str): File path where the first resampled raster will be saved.
        resampled_path2 (str): File path where the second resampled raster will be saved.
        target_resolution (float): The desired output resolution in meters.

    Returns:
        tuple: A tuple (raster1, raster2), where one or both rasters may have been resampled to ensure matching CRS and resolution.

    Raises:
        ValueError: If the CRS of the two rasters do not match.
    """
    crs1 = raster1.crs().authid()
    crs2 = raster2.crs().authid()

    # Step 1: Check and handle CRS mismatch
    if crs1 != crs2:
        print(f"CRS mismatch detected: {crs1} vs {crs2}. Reprojecting raster2 to match raster1.")
        
        # Use GDAL to reproject the second raster to the first's CRS
        temp_reprojected_path = "temp/reprojected_lulc_temp.tif"
        gdal.Warp(
            temp_reprojected_path,
            path_raster2,
            options=gdal.WarpOptions(
                format="GTiff",
                srcSRS=crs2,
                dstSRS=crs1,
                outputType=gdal.GDT_Float32,
                resampleAlg=gdal.GRIORA_Bilinear,
                srcNodata=raster2.dataProvider().sourceNoDataValue(1),
                dstNodata=raster1.dataProvider().sourceNoDataValue(1)
            )
        )
        # Reload raster2 to get the updated CRS
        path_raster2 = temp_reprojected_path
        raster2 = load_raster(path_raster2, "reprojected_lulc")

    print("CRS check finished.")

    # Step 2: Resample both rasters to the target resolution
    print(f"Resampling both rasters to {target_resolution}m resolution.")
    
    # Resample the first raster
    gdal.Warp(
        resampled_path1,
        path_raster1,
        options=gdal.WarpOptions(
            xRes=target_resolution,
            yRes=target_resolution,
            targetAlignedPixels=True,
            dstSRS=raster1.crs().authid(),
            resampleAlg="bilinear",
            format="GTiff",
            outputBounds=(
                raster1.extent().xMinimum(),
                raster1.extent().yMinimum(),
                raster1.extent().xMaximum(),
                raster1.extent().yMaximum(),
            ),
        )
    )

    # Resample the second raster
    gdal.Warp(
        resampled_path2,
        path_raster2,
        options=gdal.WarpOptions(
            xRes=target_resolution,
            yRes=target_resolution,
            targetAlignedPixels=True,
            dstSRS=raster2.crs().authid(),
            resampleAlg="near",
            format="GTiff",
            outputBounds=(
                raster2.extent().xMinimum(),
                raster2.extent().yMinimum(),
                raster2.extent().xMaximum(),
                raster2.extent().yMaximum(),
            ),
        )
    )

    raster1 = load_raster(resampled_path1, "resampled_raster1")
    raster2 = load_raster(resampled_path2, "resampled_raster2")

    print("Resample finished.")
    return raster1, raster2


def transform_to_raster(vector_layer, reference_raster, output_path, target_resolution):
    """
    Converts a vector layer to a raster using the properties of a reference raster and a fixed resolution.

    This function rasterizes the input vector layer, aligning it with the spatial extent
    and coordinate reference system of the provided reference raster, and using a specified
    fixed resolution. The output raster is saved to the specified path and loaded for
    further processing.

    Args:
        vector_layer: The vector layer to be rasterized.
        reference_raster: The reference raster whose extent and CRS will be used.
        output_path (str): The file path where the output raster will be saved.
        target_resolution (float): The desired output resolution in the units of the CRS.

    Returns:
        RasterLayer: The loaded raster layer created from the rasterized vector data.

    Raises:
        Exception: If rasterization fails or input parameters are invalid.

    Note:
        Requires GDAL and a compatible raster/vector data environment.
    """
    gdal.Rasterize(
        output_path,
        vector_layer.source(),
        options=gdal.RasterizeOptions(
            format="GTiff",
            outputType=gdal.GDT_Byte,
            burnValues=[1],
            noData=0,
            initValues=[0],
            xRes=target_resolution,
            yRes=target_resolution,
            outputBounds=(
                reference_raster.extent().xMinimum(),
                reference_raster.extent().yMinimum(),
                reference_raster.extent().xMaximum(),
                reference_raster.extent().yMaximum(),
            ),
            targetAlignedPixels=True,
            outputSRS=reference_raster.crs().authid(),
            creationOptions=["COMPRESS=LZW"],
        ),
    )
    print("Point transformed to raster.")
    return load_raster(output_path, "flood_raster")


def raster_to_dataframe(raster_layer):
    """
    Converts a raster layer to a pandas DataFrame with pixel values and their corresponding spatial coordinates.

    Parameters:
        raster_layer (QgsRasterLayer): The raster layer to convert.

    Returns:
        pandas.DataFrame: A DataFrame with columns:
            - 'value': The raster pixel value (with NoData replaced by np.nan).
            - 'x': The x-coordinate of the pixel center.
            - 'y': The y-coordinate of the pixel center.
    """
    
    provider = raster_layer.dataProvider()
    nodata = provider.sourceNoDataValue(1)

    extent = raster_layer.extent()
    width = raster_layer.width()
    height = raster_layer.height()
    block = provider.block(1, extent, width, height)

    array_2d = np.array(
        [[block.value(x, y) for x in range(width)] for y in range(height)]
    )

    flat_array = array_2d.flatten()

    if nodata is not None:
        flat_array = np.where(np.isclose(flat_array, nodata), np.nan, flat_array)

    x_origin = extent.xMinimum()
    y_origin = extent.yMaximum()
    pixel_width = raster_layer.rasterUnitsPerPixelX()
    pixel_height = raster_layer.rasterUnitsPerPixelY()

    x_coords = np.array(
        [x_origin + (i % width) * pixel_width for i in range(width * height)]
    )

    y_coords = np.array(
        [y_origin - (i // width) * pixel_height for i in range(width * height)]
    )

    df = pd.DataFrame({"value": flat_array, "x": x_coords, "y": y_coords})


    return df

def create_final_dataframe(dtm_df, lulc_df, flood_df, river_df, tributaries_df, basin_df):
    """
    Merges DTM, LULC, Flood, River, and Microbasin DataFrames into a single DataFrame.

    Args:
        dtm_df (pd.DataFrame): DataFrame containing DTM data.
        lulc_df (pd.DataFrame): DataFrame containing LULC data.
        flood_df (pd.DataFrame): DataFrame containing Flood data.
        river_df (pd.DataFrame): DataFrame containing river distance data.

    Returns:
        pd.DataFrame: A single DataFrame with all features.
    """
    # Rename value columns to their final names before merging to avoid conflicts.
    dtm_df = dtm_df.rename(columns={'value': 'dtm_value'})
    lulc_df = lulc_df.rename(columns={'value': 'lulc_code'})
    flood_df = flood_df.rename(columns={'value': 'flood_binary'})
    river_df = river_df.rename(columns={'value': 'dist_to_river'})
    tributaries_df = tributaries_df.rename(columns={'value': 'dist_to_tributaries'})
    basin_df = basin_df.rename(columns={'value': 'is_basin'})

    # Start with DTM and merge the other DataFrames sequentially.
    final_df = dtm_df
    final_df = pd.merge(final_df, lulc_df, on=['x', 'y'], how='outer')
    final_df = pd.merge(final_df, flood_df, on=['x', 'y'], how='outer')
    final_df = pd.merge(final_df, river_df, on=['x', 'y'], how='outer')
    final_df = pd.merge(final_df, tributaries_df, on=['x', 'y'], how='outer')
    final_df = pd.merge(final_df, basin_df, on=['x', 'y'], how='outer')

    # A value of NaN in 'flood_binary' or 'is_microbacin' means no flood or not in a microbasin, so fill with 0
    final_df['flood_binary'] = final_df['flood_binary'].fillna(0)
    final_df['is_basin'] = final_df['is_basin'].fillna(0)
    
    # Drop rows where any of the core data columns are NaN to ensure consistency
    final_df.dropna(subset=['dtm_value', 'lulc_code'], how='any', inplace=True)
    
    return final_df


def calculate_distance_to_features(vector_layer, reference_raster, output_path, target_resolution):
    """
    Calculates the distance from each pixel to the nearest feature in a vector layer.

    Args:
        vector_layer: The vector layer containing the features (e.g., rivers).
        reference_raster: The raster used for extent and CRS.
        output_path (str): The file path for the output distance raster.
        target_resolution (float): The desired output resolution in meters.

    Returns:
        QgsRasterLayer: The loaded raster layer with distance values.
    """
    print(f"Calculating distance to features in layer: {vector_layer.name()}")
    
    # Use a consistent NoData value for all raster operations
    NODATA_VALUE = -9999.0

    # Step 1: Create an empty raster to serve as a base for the distance calculation
    empty_raster_path = "temp/empty_raster.tif"
    gdal.Rasterize(
        empty_raster_path,
        vector_layer.source(),
        options=gdal.RasterizeOptions(
            format="GTiff",
            outputType=gdal.GDT_Byte,
            burnValues=[1],
            noData=0,
            xRes=target_resolution,
            yRes=target_resolution,
            outputBounds=(
                reference_raster.extent().xMinimum(),
                reference_raster.extent().yMinimum(),
                reference_raster.extent().xMaximum(),
                reference_raster.extent().yMaximum(),
            ),
            targetAlignedPixels=True,
            outputSRS=reference_raster.crs().authid(),
            creationOptions=["COMPRESS=LZW"],
        )
    )

    # Step 2: Open the newly created raster file and get the raster band
    input_ds = gdal.Open(empty_raster_path, gdalconst.GA_ReadOnly)
    if input_ds is None:
        raise IOError(f"Could not open file: {empty_raster_path}")
    input_band = input_ds.GetRasterBand(1)
    
    # Step 3: Create the output raster dataset
    driver = gdal.GetDriverByName("GTiff")
    output_ds = driver.Create(
        output_path, 
        input_band.XSize, 
        input_band.YSize, 
        1, 
        gdal.GDT_Float32
    )
    if output_ds is None:
        raise IOError(f"Could not create file: {output_path}")

    # Set projection and geotransform from the input raster
    output_ds.SetProjection(input_ds.GetProjection())
    output_ds.SetGeoTransform(input_ds.GetGeoTransform())
    
    output_band = output_ds.GetRasterBand(1)
    output_band.SetNoDataValue(NODATA_VALUE)

    # Step 4: Call ComputeProximity with both input and output bands
    gdal.ComputeProximity(
        input_band,
        output_band,
        options=["DISTUNITS=GEO", "MAXDIST=1000000", "NODATA=-9999"],
    )

    # Step 5: Close the datasets to release file locks
    input_ds = None
    output_ds = None

    return QgsRasterLayer(output_path, "distance_raster")


def transform_vector_to_binary_raster(vector_layer, reference_raster, output_path, target_resolution):
    """
    Converts a vector layer to a binary raster (1 for feature, 0 for no feature).

    Args:
        vector_layer: The vector layer to be rasterized.
        reference_raster: The raster used for extent and CRS.
        output_path (str): The file path for the output binary raster.
        target_resolution (float): The desired output resolution in meters.

    Returns:
        RasterLayer: The loaded binary raster layer.
    """
    print(f"Rasterizing vector layer '{vector_layer.name()}' to binary format.")
    nodata = reference_raster.dataProvider().sourceNoDataValue(1)
    
    gdal.Rasterize(
        output_path,
        vector_layer.source(),
        options=gdal.RasterizeOptions(
            format="GTiff",
            outputType=gdal.GDT_Byte,
            burnValues=[1],
            noData=nodata,
            initValues=[0],
            xRes=target_resolution,
            yRes=target_resolution,
            outputBounds=(
                reference_raster.extent().xMinimum(),
                reference_raster.extent().yMinimum(),
                reference_raster.extent().xMaximum(),
                reference_raster.extent().yMaximum(),
            ),
            targetAlignedPixels=True,
            outputSRS=reference_raster.crs().authid(),
            creationOptions=["COMPRESS=LZW"],
        )
    )
    print("Vector layer successfully rasterized.")
    return load_raster(output_path, "binary_raster")
